# Akamai CPS Enrollment Creation Script

A Python script for creating a new certificate enrollment in Akamai's **Certificate Provisioning System (CPS) v2 API**, using EdgeGrid authentication. It is preconfigured for a **third-party certificate** enrollment with custom domain (SAN), contact, and organization details.

## What It Does

The script sends a `POST` request to:

```
/cps/v2/enrollments
```

to create a new CPS enrollment. It then prints a formatted summary of the response, including the enrollment ID and any pending changes, or a parsed error message if the request fails.

## Prerequisites

### Python packages

```bash
pip install requests edgegrid-python cryptography
```

### Akamai `.edgerc` file

You need a valid `.edgerc` credentials file containing your Akamai API client credentials (host, client token, client secret, access token). See [Akamai's EdgeGrid authentication docs](https://techdocs.akamai.com/developer/docs/authenticate-with-edgegrid) for details on generating one.

### API client permissions

The API client referenced in your `.edgerc` must have **read-write access to the CPS API** for the relevant contract.

## Configuration

Before running the script, update the following placeholders:

| Variable | Location | Description |
|---|---|---|
| `edgerc_path` | Top of script | Full path to your `.edgerc` file (currently set to a Windows path placeholder) |
| `section` | Top of script | The section name in your `.edgerc` file (default: `default`) |
| `CONTRACT_ID` | `queryString` | Your Akamai contract ID |
| `accountSwitchKey` | `queryString` | Your account switch key (only needed if managing another account; remove if not applicable) |
| `csr` | `enrollment_data` | Certificate Signing Request details: common name (`cn`), SANs, country, state, locality, organization |
| `dnsNames` | `enrollment_data.networkConfiguration` | List of hostnames to be covered by the certificate |
| `adminContact` / `techContact` | `enrollment_data` | Administrative and technical contact details required by the CA |
| `org` | `enrollment_data` | Organization details associated with the certificate |

> ⚠️ **All `XXXXXX` placeholder values must be replaced with real data before running the script.** The request will fail or be rejected by the CA otherwise.

### Optional settings

These are commented out by default and can be enabled as needed:

- `deploy-not-before` / `deploy-not-after` (query string) — restrict the deployment window for the certificate.
- `assignedSlots` — manually assign specific deployment slots.
- `deploymentSchedule` — schedule the certificate's `notBefore` / `notAfter` deployment dates.

## Key Enrollment Settings

| Setting | Value | Meaning |
|---|---|---|
| `certificateType` | `third-party` | Certificate is issued by an external CA, not Akamai/CPS-managed |
| `ra` | `third-party` | Registration authority is third-party |
| `validationType` | `third-party` | No CPS-managed domain validation is performed |
| `changeManagement` | `True` | Prevents automatic deployment to production; changes must be manually deployed |
| `secureNetwork` | `enhanced-tls` | Deploys on Akamai's Enhanced TLS network |
| `sniOnly` | `True` | Certificate is served using SNI-only delivery |
| `cloneDnsNames` | `False` | DNS names are explicitly defined rather than cloned from the CSR |

These values can be changed to suit your certificate type (`san`, `single`, `wildcard`, `wildcard-san`, or `third-party`) and validation needs (`dv`, `ev`, `ov`, or `third-party`).

## Usage

1. Update the configuration values described above.
2. Run the script:

```bash
python create_enrollment.py
```

3. Review the console output.

## Output

### On success (HTTP 200/201/202)

The script prints:
- The full JSON response
- The enrollment ID (`enrollment`)
- Any pending changes (`changes`) — these typically need to be acknowledged/deployed separately in CPS

### On failure

The script attempts to parse the error as JSON first, printing the `title`, `detail`, and `type` fields. If the response isn't valid JSON, it falls back to parsing a plaintext `ApiError(...)` format and prints the `title`, `detail`, `type`, and `source`.

If the error title is **"Invalid Contract"**, the script prints hints suggesting you verify the `CONTRACT_ID` and `accountSwitchKey` values are correct for the API client being used.

## Notes & Security

- **Never commit your `.edgerc` file or real contact/organization details to version control.**
- The `accountSwitchKey` is only required when the API client is making calls on behalf of a different account than the one the credentials belong to; omit the parameter entirely if not needed.
- Because `changeManagement` is set to `True`, creating the enrollment will **not** automatically push the certificate to production — a separate deployment step is required in CPS.
- This script does not handle CSR generation or private key creation; it assumes you intend to use CPS's CSR generation for a third-party-issued certificate, per the `thirdParty` configuration block.

## References

- [Akamai CPS v2 API documentation](https://techdocs.akamai.com/cps/reference/api)
- [EdgeGrid authentication for Python](https://github.com/akamai/AkamaiOPEN-edgegrid-python)
