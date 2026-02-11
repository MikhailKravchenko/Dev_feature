# Snippet: helm upgrade --install

Один job для деплоя через Helm.

```yaml
deploy:
  stage: deploy
  image:
    name: alpine/helm:latest
    entrypoint: [""]
  script:
    - helm upgrade --install "$RELEASE_NAME" "$CHART_PATH" -n "$NAMESPACE" -f "$VALUES_FILE" --wait
  variables:
    RELEASE_NAME: "myapp"
    CHART_PATH: "./chart"
    NAMESPACE: "production"
    VALUES_FILE: "values-prod.yaml"
```

С передачей тега образа из CI:

```yaml
  script:
    - helm upgrade --install "$RELEASE_NAME" "$CHART_PATH" -n "$NAMESPACE" -f "$VALUES_FILE" --set image.tag="$CI_COMMIT_SHORT_SHA" --wait
```

Kubeconfig из переменной (тип File в CI/CD Variables):

```yaml
deploy:
  variables:
    KUBECONFIG: $KUBE_CONFIG_CONTENT  # или файл из Variable типа File
  script:
    - helm upgrade --install ...
```
