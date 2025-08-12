import argparse
import json
import os
import sys
import time

from google.api_core import exceptions
from google.cloud.workflows import executions_v1
from google.cloud.workflows.executions_v1.types import Execution


def execute_workflow(
    project_id: str,
    region: str,
    workflow_name: str,
    execution_args: dict,
    poll_interval_seconds: int = 10,
) -> str:
    """
    Executes a workflow and waits for it to complete.

    Args:
        project_id: The Google Cloud project ID.
        region: The region where the workflow is deployed.
        workflow_name: The name of the workflow to execute.
        execution_args: A dictionary of arguments to pass to the workflow.
        poll_interval_seconds: The interval in seconds to poll for workflow status.

    Returns:
        The result of the workflow execution as a string.

    Raises:
        RuntimeError: If the workflow execution fails or is cancelled.
    """
    client = executions_v1.ExecutionsClient()
    parent = client.workflow_path(project_id, region, workflow_name)

    execution = Execution(argument=json.dumps(execution_args))

    try:
        response = client.create_execution(parent=parent, execution=execution)
        print(f"Created execution: {response.name}")

        # Wait for the execution to complete.
        while response.state not in (
            Execution.State.SUCCEEDED,
            Execution.State.FAILED,
            Execution.State.CANCELLED,
        ):
            time.sleep(poll_interval_seconds)
            try:
                response = client.get_execution(name=response.name)
                print(f"Execution state: {Execution.State(response.state).name}")
            except exceptions.NotFound:
                # The execution might have been deleted if it completed very quickly.
                # This is unlikely for a long-running workflow but handled for robustness.
                print(f"Execution {response.name} not found. It may have completed and been deleted.")
                break

        if response.state == Execution.State.SUCCEEDED:
            print(f"Execution {response.name} succeeded.")
            return response.result
        else:
            error_message = f"Execution {response.name} did not succeed. Final state: {Execution.State(response.state).name}"
            if response.error:
                error_message += f"\nError payload: {response.error.payload}"
            print(error_message, file=sys.stderr)
            raise RuntimeError(error_message)

    except exceptions.GoogleAPICallError as e:
        print(f"An API error occurred while executing the workflow: {e}", file=sys.stderr)
        raise


def main():
    """
    Main function to parse arguments and trigger the workflow.
    """
    parser = argparse.ArgumentParser(
        description="Orchestrate the longform news video generation workflow."
    )
    parser.add_argument(
        "--topic", type=str, required=True, help="The topic for the news video."
    )
    parser.add_argument(
        "--env",
        type=str,
        default="dev",
        help="The environment to run in (e.g., dev, prod).",
    )

    args = parser.parse_args()

    # --- Configuration ---
    # It's recommended to manage these configurations via environment variables.
    project_id = os.environ.get("PROJECT_ID", "carbon-broker-466711-d0")
    region = os.environ.get("REGION", "us-central1")
    workflow_name = os.environ.get("WORKFLOW_NAME", "longform-black-news-workflow")

    # URLs for the microservices, fetched from environment variables
    required_urls = {
        "scriptwriter_url": os.environ.get("SCRIPTWRITER_URL"),
        "media_sourcing_url": os.environ.get("MEDIA_SOURCING_URL"),
        "narrator_url": os.environ.get("NARRATOR_URL"),
        "video_assembly_url": os.environ.get("ASSEMBLY_URL"),
        "uploader_url": os.environ.get("UPLOADER_URL"),
        "error_handler_url": os.environ.get("ERROR_HANDLER_URL"),
        "logger_url": os.environ.get("LOGGER_URL"),
    }

    missing_urls = [name for name, url in required_urls.items() if not url]
    if missing_urls:
        print(f"Error: Missing required environment variables for URLs: {', '.join(missing_urls)}", file=sys.stderr)
        sys.exit(1)

    # --- Prepare workflow arguments ---
    workflow_args = {
        "env": args.env,
        "topic": args.topic,
        **required_urls,
    }

    # --- Execute Workflow ---
    try:
        result = execute_workflow(project_id, region, workflow_name, workflow_args)
        print("\nWorkflow finished successfully.")
        print("Result:")
        print(json.loads(result))
    except (RuntimeError, exceptions.GoogleAPICallError) as e:
        print(f"\nWorkflow execution failed.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()