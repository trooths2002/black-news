# Operations Guide: Deploying the Workflow

This guide provides the necessary commands and checks to deploy and troubleshoot the Google Cloud Workflow via Cloud Build.

## 1. Pre-flight Checks

Before submitting a build, run these checks from the project root to prevent common errors.

### Check `cloudbuild.yaml` for invalid `${...}` tokens

This command should only output `${_KEY}` variables from the `env:` block. Any other `${...}` token is an error.

```powershell
Select-String -Path .\cloudbuild.yaml -Pattern '\$\{.*?\}' -AllMatches
```

### Check `workflow.tpl.yaml` for unsubstituted template variables

This command ensures no `${ALL_CAPS_VARS}` remain in the template. It should produce **no output**. Workflow-native expressions like `${args.env}` are ignored and are correct.

```powershell
Select-String -Path .\black-news\gcp-news-pipeline\workflow.tpl.yaml -Pattern '\$\{([A-Z_][A-Z0-9_]*)\}' -AllMatches
```

## 2. Submitting the Build

Use this command to trigger the Cloud Build pipeline. It relies on the substitutions already defined in `cloudbuild.yaml`.

```powershell
gcloud builds submit --config cloudbuild.yaml --project=carbon-broker-466711-d0
```

**Note on `.gcloudignore`**: A `.gcloudignore` file is present in the repository. This is critical for keeping build submission times fast by excluding unnecessary files like the `venv/` directory.

## 3. Monitoring the Build

If the submission is successful, Cloud Build will return a **Build ID**. Use it to get logs.

```powershell
# Replace BUILD_ID with the actual ID from the previous command
gcloud builds log BUILD_ID --project=carbon-broker-466711-d0
```

You can also view live logs here: [https://console.cloud.google.com/cloud-build/builds?project=carbon-broker-466711-d0](https://console.cloud.google.com/cloud-build/builds?project=carbon-broker-466711-d0)

## 4. Troubleshooting

*   **Submit-time `INVALID_ARGUMENT` (No Build ID)**: This is a pre-flight validation error. It means there is an invalid `${...}` token in `cloudbuild.yaml` that Cloud Build tried to parse as a substitution. Run the pre-flight checks to find it.
*   **Build Failure with `envsubst: not found`**: The `gcr.io/google.com/cloudsdktool/cloud-sdk` image includes `gettext-base` which provides `envsubst`. If this error appears, the base image may have changed. You can fix it by uncommenting the `apt-get` line in the `cloudbuild.yaml` build step.
*   **Workflow Deployment Fails**: If the build runs but the `gcloud workflows deploy` step fails, check the build logs. The error is likely in the rendered `workflow.rendered.yaml` (e.g., a syntax error from a missing variable) or an IAM permission issue with the `--service-account`.

## 5. Smoke Test Execution

Once the workflow is deployed successfully, run this command to trigger a test execution.

```powershell
gcloud workflows execute longform-black-news --location=us-central1 --project=carbon-broker-466711-d0 --data='{"env":"prod","topic":"Test execution from Gemini CLI"}'
```
