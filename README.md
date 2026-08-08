# Artifact Registry (Terraform + GitHub Actions)

Provisions a single GCP Artifact Registry repository. Apply locally, or trigger via GitHub Actions.

## Files

- `main.tf` — provider + `google_artifact_registry_repository` resource
- `variables.tf` / `outputs.tf`
- `terraform.tfvars.example` — copy to `terraform.tfvars` for local runs (gitignored)
- `.github/workflows/terraform-apply.yml` — manual workflow that runs `terraform apply`

## Run locally

```
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply
```

## Run via GitHub Actions

The workflow (`Terraform Apply - Artifact Registry`) is manual — trigger it from the **Actions** tab, "Run workflow".

### One-time setup

1. Create a GCP service account with permission to manage Artifact Registry:

   ```
   gcloud iam service-accounts create tf-artifact-registry \
     --project=<PROJECT_ID> \
     --display-name="Terraform Artifact Registry CI"

   gcloud projects add-iam-policy-binding <PROJECT_ID> \
     --member="serviceAccount:tf-artifact-registry@<PROJECT_ID>.iam.gserviceaccount.com" \
     --role="roles/artifactregistry.admin"
   ```

2. Create and download a JSON key for that service account:

   ```
   gcloud iam service-accounts keys create key.json \
     --iam-account=tf-artifact-registry@<PROJECT_ID>.iam.gserviceaccount.com
   ```

3. In the GitHub repo, go to **Settings > Secrets and variables > Actions** and add:

   | Secret name | Value |
   |---|---|
   | `GCP_SA_KEY` | full contents of `key.json` |
   | `GCP_PROJECT_ID` | your GCP project ID |

   Delete the local `key.json` after adding it as a secret — don't commit it.

4. Push this repo to GitHub, go to the **Actions** tab, select **Terraform Apply - Artifact Registry**, and click **Run workflow**.

### Notes

- State is local to the runner (no remote backend configured) — each workflow run starts from a fresh `terraform init`. Fine for a single resource like this; if you add more resources or run this repeatedly, add a GCS backend so state persists between runs.
- Region, repository name, and format come from `variables.tf` defaults; override by adding `TF_VAR_*` env vars or a checked-in `.tfvars` to the workflow if needed.
