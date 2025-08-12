# Gemini Project Configuration

This document outlines specific configurations and guidelines for the Gemini-powered news automation project.

## Data Sourcing Guidelines

All news content used for script generation **must come from reputable sources**. Fabrication of news or any form of misinformation is strictly prohibited. The integrity and accuracy of the information are paramount.

## Google Cloud Project Details

*   **Google Cloud Project ID:** carbon-broker-466711-d0

## Deployment Status

The project has been successfully deployed to Google Cloud Platform. All Cloud Functions, the Workflow, and the Cloud Scheduler job are active and operational.

## Cost Implications

Using these services will incur costs, all billed directly through your Google Cloud Platform (GCP) account. There are no direct external services integrated into this workflow that would incur separate billing outside of GCP.

**Main cost drivers include:**

*   **Gemini API (LLM and Text-to-Speech):** Billed based on the number of characters processed for input/output (LLM) and synthesized (TTS). The `scriptwriter` function currently uses `gemini-1.5-flash-001` but may require further configuration in your GCP project to function correctly.
*   **Cloud Functions:** Billed based on invocations, CPU time, and memory. Free tier available.
*   **Cloud Storage:** Billed based on data stored, network egress, and operations.
*   **Cloud Workflows:** Billed based on the number of steps executed.
*   **Cloud Scheduler:** Billed per job execution. Free tier available.
*   **Transcoder API:** Billed based on the duration of the output video generated.
*   **Google Drive API:** The `uploader` function integrates with Google Drive. Costs may apply if you exceed free tier limits for Google Drive storage. Authentication is handled via a service account key stored in Google Secret Manager.

## Cloud-Native Architecture

This project has been architected as a fully cloud-native application on Google Cloud Platform to ensure scalability, resilience, and maintainability.

*   **Orchestration:** **Cloud Workflows** is used to define and execute the end-to-end video generation process. The workflow is defined declaratively in `workflow.yaml`.
*   **Business Logic:** Each distinct step in the process (e.g., scriptwriting, narration, video assembly) is encapsulated in a separate, stateless **Cloud Function**.
*   **Scheduling:** **Cloud Scheduler** is used to automatically trigger the workflow on a fixed schedule (e.g., every 8 hours).
*   **Artificial Intelligence:** **Gemini API** services, including Large Language Models (for scriptwriting) and Text-to-Speech (for narration), provide the core intelligence.
*   **Video Processing:** The **Transcoder API** is used for efficient, serverless video assembly.
*   **Storage:** **Cloud Storage** is used for intermediate storage of media assets, and **Google Drive** is the final destination for the completed videos.

## Security and IAM

To adhere to the principle of least privilege, each component in this architecture should run with a dedicated service account and the minimum necessary IAM roles.

*   **Cloud Scheduler Service Account**: Needs the `Workflows Invoker` (`roles/workflows.invoker`) role to be able to trigger the workflow.
*   **Cloud Workflow Service Account**: Needs the `Cloud Functions Invoker` (`roles/cloudfunctions.invoker`) role on each of the agent Cloud Functions it calls.
*   **Cloud Function Service Accounts**:
    *   **Scriptwriter & Narrator Agents**: `Vertex AI User` role to access generative models, or specific roles for Gemini API if different.
    *   **Media Sourcing Agent**: `Storage Object Creator` to save media files to a Cloud Storage bucket.
    *   **Video Assembly Agent**: `Transcoder Editor` to create jobs, and `Storage Object Admin` on the relevant buckets to read inputs and write outputs.
    *   **Uploader Agent**: `Storage Object Viewer` to read the final video from Cloud Storage and permissions for the Google Drive API (which requires OAuth 2.0 configuration).

## Roadmap to Production Readiness - Technical Deep Dive

This section provides a more technical breakdown of the steps required to evolve the current news automation pipeline into a fully production-ready system, focusing on implementation details and potential integrations.

### 1. Content Generation (Scriptwriter Agent)

*   **LLM Prompt Engineering:**
    *   **Dynamic Prompting:** Implement logic to dynamically construct prompts based on real-time news events, trending topics, or user-defined keywords.
    *   **Few-shot Learning:** Provide the Gemini API with examples of high-quality news scripts to guide its generation towards desired styles and structures.
    *   **Iterative Refinement:** Implement a feedback loop where generated scripts can be reviewed (human or automated) and the feedback used to refine prompts or fine-tune the model (if applicable).
*   **News Source Integration:**
    *   **RSS Feed Parsing (Primary Sourcing):** Develop a component to parse RSS feeds from reputable news outlets, focusing on black/African geopolitics and trending news.
    *   **API-based Sourcing (Future Consideration):** Integration with news APIs (e.g., NewsAPI, Google News API) can be considered for future enhancements to fetch structured news data.
    *   **Web Scraping (with caution):** For sources without APIs, implement web scraping (e.g., using Beautiful Soup, Scrapy) with robust error handling, rate limiting, and adherence to `robots.txt` and terms of service.
*   **Content Filtering and Summarization:**
    *   **Keyword Extraction:** Use NLP techniques (e.g., spaCy, NLTK) to extract key entities and topics from raw news data.
    *   **Sentiment Analysis:** Analyze the sentiment of news articles to ensure appropriate tone in the generated script.
    *   **Summarization Models:** Potentially use smaller LLMs or specialized summarization models to condense lengthy articles before feeding them to the main scriptwriter LLM.
*   **Fact-Checking Integration:**
    *   **Cross-referencing:** Implement automated checks against multiple trusted sources for key facts and figures using best-in-class methodologies and potentially integrating with YouTube and other news source feeds.
    *   **Knowledge Graph Integration:** Leverage knowledge graphs (e.g., Google Knowledge Graph, Wikidata) to verify factual claims.

### 2. Media Sourcing (Media Sourcing Agent)

*   **Stock Media API Integration:**
    *   Integrate with APIs of stock video/image providers (e.g., Pexels API, Pixabay API, Shutterstock API, Getty Images API). This involves managing API keys, handling authentication, and parsing API responses.
    *   Implement search queries based on keywords extracted from the script.
*   **Public Domain/Creative Commons Sourcing:**
    *   Develop modules to search and download media from public domain archives (e.g., Internet Archive, Wikimedia Commons) or Creative Commons licensed content.
*   **Metadata Extraction and Management:**
    *   Extract relevant metadata (e.g., duration, resolution, aspect ratio, licensing information) from sourced media.
    *   Store media metadata in a database (e.g., Cloud Firestore, Cloud SQL) for efficient lookup and management.
*   **Media Processing Pipeline:**
    *   **Image/Video Resizing and Cropping:** Utilize image processing libraries (e.g., Pillow, OpenCV) or cloud services (e.g., Cloud Vision API for smart cropping) to prepare media for video assembly.
    *   **Format Conversion:** Ensure all media is in compatible formats for the Transcoder API.

### 3. Narration (Narrator Agent)

*   **Advanced TTS Configuration:**
    *   **Voice Selection:** Implement logic to select specific voices based on script content or user preferences, specifically a black professional female voice.
    *   **SSML Implementation:** Programmatically insert SSML tags into the script to control speech attributes (e.g., `<break time="500ms"/>`, `<prosody rate="slow">`, `<emphasis level="strong">`).
    *   **Custom Pronunciation:** Define custom pronunciations for specific terms or names using SSML.
*   **Audio Post-processing:**
    *   **Normalization:** Ensure consistent audio levels across all generated narration.
    *   **Noise Reduction:** Apply basic noise reduction techniques if necessary.

### 4. Video Assembly (Video Assembly Agent)

*   **Dynamic Video Composition:**
    *   **Scene Management:** Develop a robust scene management system to map script segments to media assets and narration.
    *   **Timeline Generation:** Programmatically generate a video timeline, specifying the order, duration, and transitions for each element.
    *   **Text Overlays:** Implement dynamic text overlays for titles, lower thirds, and captions, potentially using templates, ensuring proper credit is given in the video in small text font.
*   **Transcoder API Workflow:**
    *   **Job Configuration:** Dynamically configure Transcoder API jobs with precise input/output settings, including codecs, resolutions, bitrates, and audio tracks.
    *   **Overlay Management:** Utilize Transcoder API's overlay features for branding, watermarks, or dynamic text.
    *   **Error Handling and Monitoring:** Implement robust error handling for Transcoder jobs and monitor their progress.
*   **Music Integration:**
    *   **Royalty-Free Music Library:** Integrate with a library of royalty-free background music.
    *   **Audio Mixing:** Control the volume levels of narration and background music to ensure clarity.

### 5. Uploader (Uploader Agent)

*   **Google Drive API Integration (Primary Upload Target):**
    *   **Service Account Authentication:** Use a service account with appropriate permissions for programmatic access to Google Drive.
    *   **File Uploads:** Upload the final video file to a designated Google Drive folder.
    *   **Permissions Management:** Set appropriate sharing permissions for the uploaded video.
*   **YouTube Posting (Manual for now):**
    *   The final video will be uploaded to Google Drive, from where manual YouTube posting can be performed.
    *   Future integration with YouTube Data API can be considered for automated uploads, thumbnail uploads, and playlist management.

### 6. Monitoring and Alerting

*   **Custom Metrics:** Define and export custom metrics from Cloud Functions (e.g., script generation time, media sourcing success rate, video assembly duration) to Cloud Monitoring.
*   **Log-based Metrics and Alerts:** Create log-based metrics and alerts in Cloud Monitoring to detect specific error patterns or anomalies in Cloud Logging.
*   **Dashboard Visualization:** Build custom dashboards in Cloud Monitoring to visualize key performance indicators (KPIs) of the workflow.
*   **Integration with Notification Services:** Configure Cloud Monitoring alerts to send notifications to services like PagerDuty, Slack, or custom webhooks.

### 7. Cost Management

*   **Detailed Cost Analysis:** Regularly analyze GCP billing reports, focusing on cost drivers identified in the "Cost Implications" section.
*   **Resource Optimization:**
    *   **Cloud Functions:** Optimize memory and CPU allocation for each function based on actual usage.
    *   **Cloud Storage:** Implement appropriate storage classes (e.g., Nearline, Coldline) for different data retention needs.
    *   **Transcoder API:** Optimize Transcoder API usage by selecting appropriate presets and avoiding unnecessary re-encodings.
*   **Budget Alerts:** Set up budget alerts in GCP to be notified of unexpected cost spikes.

### 8. Scalability and Resilience

*   **Load Testing:** Conduct load testing on individual Cloud Functions and the entire workflow to identify bottlenecks and ensure performance under expected load.
*   **Auto-scaling Configuration:** Ensure Cloud Functions and other scalable services are configured for appropriate auto-scaling.
*   **Idempotency:** Design functions to be idempotent where possible to prevent unintended side effects from retries.
*   **Dead-Letter Queues (DLQs):** Implement DLQs for asynchronous operations to capture and handle messages that fail processing.

This technical deep dive provides a comprehensive roadmap for transforming the current infrastructure into a fully production-ready, intelligent news video automation pipeline. The next step is to gather specific requirements and preferences from the user to begin implementing these enhancements.