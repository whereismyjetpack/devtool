def fhr(template):
    template = """
---
apiVersion: flux.weave.works/v1beta1
kind: HelmRelease
metadata:
  name: {{ release_name }}
  namespace: {{ namespace }}
  annotations:
{%- if flux_automated %}
    flux.weave.works/automated: "true"
{%- else %}
    flux.weave.works/automated: "false"
{%- endif %}
spec:
  resetValues: true
  chart:
    repository: {{ helm_repository }}
    name: {{ chart_name }}
{%- if chart_version is defined %}
    version: {{ chart_version }}
{%- endif %}
  releaseName: {{ release_name }}
  values:
    {{ values| indent(4) }}
"""
    return template
