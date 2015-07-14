google-cloud-sdk/bin/gcloud auth activate-service-account \
    --key-file "${GAE_CLIENT_KEY_JSON_FILE}"
google-cloud-sdk/bin/gcloud \
    --project "${GAE_PROJECT_ID}" \
    preview app deploy \
    --version "${GAE_VERSION_LABEL}" \
    --quiet \
    "app.yaml"