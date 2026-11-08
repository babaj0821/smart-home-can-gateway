# Publishing to GitHub

This repository is organized for an initial GitHub commit, but it contains experimental embedded/IoT code. Review the source, security settings, and rights to publish before creating a **public** repository.

## 1. Review and verify locally

From the repository root:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q architectures tests
```

These commands check Python syntax and the reconstructed telemetry queue only; they do **not** exercise CAN hardware, ThingsBoard Edge, outage recovery, or the ThingsBoard server.

Before committing, confirm the repository contains **no** deployed tokens, `.env` files, logs, runtime scenario databases, personal data, or proprietary material you are not authorized to share. If any values in an original archive were real deployed credentials, rotate them; the uploader reports that shared examples were intentionally anonymized. Review [Assumptions and open items](docs/assumptions-and-open-items.md) and [Publication and redaction review](docs/publication-review.md). The uploader intentionally anonymized device protocol constants; do not publish the private originals.

## 2. Create a repository and make the first commit

After extracting this folder and entering it:

```bash
git init
git add .
git status --short
# Inspect staged files carefully, especially config/, examples/, and docs/diagrams/.
git commit -m "Add CAN smart-home gateway architecture prototypes and documentation"
git branch -M main
```

Create an **empty** repository in your GitHub account, then connect and push it with the URL displayed by GitHub for your repository:

```bash
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main
```

`<YOUR_GITHUB_REPOSITORY_URL>` is a placeholder. Do not paste it literally; replace it with your actual HTTPS or SSH remote URL.

## 3. Final publication checklist

- Check the root [`README.md`](README.md), [four-way comparison](docs/architecture-comparison.md), [organizational selection guide](docs/organization-selection-guide.md), [central configuration guide](config/README.md), and all four architecture READMEs render correctly on GitHub. **04 — ThingsBoard Edge** was tried in the internship but is **documentation-only in this repository until its actual implementation files are pushed**.
- Set the repository visibility intentionally; **private** is a good initial setting when ownership or device details are uncertain.
- The modified upstream gateway service has an Apache-2.0 license copy under its own folder. Add a **separate project-wide license** only if you have rights to license the remaining code and images.
- Validate **whichever architecture the adopting organization chooses** on its own hardware before presenting it as production-ready. The repository describes four tested research alternatives rather than a universal winner; do not advertise Edge as runnable from this archive until its files are supplied.
- Keep `.env` out of Git. The committed `.env.example` files are under **root `config/`**, alongside architecture 03 Gateway JSON, its Compose reference and the hardware Device Tree source. These templates contain anonymized placeholder values, not production credentials. From `config/03-scenario-connector/`, run the Compose commands in the [configuration guide](config/README.md).
