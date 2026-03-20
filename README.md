# Google Play Publish Action

A GitHub Action to publish Android app bundles (`.aab`) to Google Play Console via the Android Publisher API v3.

## Features

- Publishes to any release track: `internal`, `alpha`, `beta`, or `production`
- Supports all release statuses: `draft`, `completed`, `inProgress`, `halted`
- Secure credential handling — GPG passphrase is never exposed in the process list
- Validates configuration before attempting to publish
- Clear, structured log output for easy debugging

---

## Prerequisites

### 1. Google Play Service Account

1. Open [Google Play Console](https://play.google.com/console) → **Setup** → **API access**
2. Link to a Google Cloud project and create a service account with the **Release Manager** role
3. Download the JSON key file for the service account

### 2. Encrypt the Service Account Key with GPG

```bash
gpg --symmetric --cipher-algo AES256 --batch \
  --passphrase "YOUR_PASSPHRASE" \
  --output service-account.json.asc \
  service-account.json
```

### 3. Add GitHub Secrets

| Secret name                   | Value                                         |
|-------------------------------|-----------------------------------------------|
| `PLAYSTORE_ENCRYPTED_FILE`    | Contents of `service-account.json.asc` (run `cat service-account.json.asc`) |
| `PLAYSTORE_DECRYPTION_PWD`    | The passphrase used to encrypt the file       |

---

## Usage

Create a publish config file (e.g., `publish_config.json`) at the root of your repo:

```json
{
  "package_name": "com.example.myapp",
  "app_file_path": "app/build/outputs/bundle/release/app-release.aab",
  "track": "internal",
  "version_code": 42,
  "release_name": "2.1.0",
  "release_status": "completed",
  "release_notes": [
    {
      "language": "en-US",
      "text": "Bug fixes and performance improvements."
    },
    {
      "language": "fr-FR",
      "text": "Corrections de bugs et améliorations des performances."
    }
  ]
}
```

Then add the action to your workflow:

```yaml
name: Publish to Google Play

on:
  push:
    branches: [main]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build release AAB
        run: ./gradlew bundleRelease

      - name: Sign AAB
        # ... your signing step here

      - name: Publish to Google Play
        uses: codingloop/google-play-publish@main
        with:
          config_file: publish_config.json
          playstore_encrypted_file: ${{ secrets.PLAYSTORE_ENCRYPTED_FILE }}
          playstore_decryption_pwd: ${{ secrets.PLAYSTORE_DECRYPTION_PWD }}
```

---

## Inputs

| Input                        | Required | Description                                                  |
|------------------------------|----------|--------------------------------------------------------------|
| `config_file`                | Yes      | Path to the JSON config file (relative to `GITHUB_WORKSPACE`) |
| `playstore_encrypted_file`   | Yes      | GPG-encrypted service account JSON as a string               |
| `playstore_decryption_pwd`   | Yes      | Passphrase to decrypt the service account file               |

## Outputs

| Output    | Description                          |
|-----------|--------------------------------------|
| `message` | `"Successful"` on a successful run   |

---

## Configuration Reference

| Field            | Type     | Required | Description                                                     |
|------------------|----------|----------|-----------------------------------------------------------------|
| `package_name`   | string   | Yes      | App's package name (e.g. `com.example.myapp`)                  |
| `app_file_path`  | string   | Yes      | Path to the `.aab` file, relative to `GITHUB_WORKSPACE`        |
| `track`          | string   | Yes      | Release track: `internal`, `alpha`, `beta`, or `production`    |
| `version_code`   | integer  | Yes      | Android version code (must be greater than the last upload)    |
| `release_name`   | string   | Yes      | Human-readable release name (e.g. `"2.1.0"`)                  |
| `release_status` | string   | Yes      | `draft`, `completed`, `inProgress`, or `halted`                |
| `release_notes`  | array    | Yes      | List of `{ "language": "...", "text": "..." }` objects         |

---

## How It Works

```
Workflow triggered
    │
    ├─ Read & validate publish_config.json
    ├─ Decrypt service account credentials (GPG via stdin)
    ├─ Build Android Publisher API v3 service
    │
    └─ PlayStorePublisher.execute()
           ├─ Create edit session
           ├─ Upload .aab file
           ├─ Update release metadata & track
           └─ Commit edit → Published
```

---

## Security

- The GPG passphrase is piped to `gpg` via **stdin** (`--passphrase-fd 0`), so it is **never visible in the process list** or system logs.
- Decrypted credential files are written to a temporary directory and deleted immediately after use, even if an error occurs.

---

## License

MIT © [Ishwar Bhat](https://github.com/codingloop)
