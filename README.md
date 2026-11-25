# Fidel AI — installable web app

This project creates a responsive AI web app that can be installed on Android
from a supported browser (PWA / Add to Home Screen).

## Features
- Responsive mobile-first chat interface
- Gemini-powered responses, with optional Google Search grounding
- Image upload and image questions
- Voice recording upload for Gemini audio understanding
- Spoken answers using browser speech synthesis
- User-managed saved memories stored locally in the browser
- Recent chat history stored locally in the browser
- PWA manifest, service worker, and app icon

## Deploy to Render
1. Create a GitHub repository and upload all files in this folder.
2. Sign in to Render and create a new Web Service from that repository.
3. Render can use the included `render.yaml` configuration.
4. In the service Environment settings, set `GEMINI_API_KEY` to your private API key.
5. Confirm `GEMINI_MODEL` is a model your Google AI account can access.
6. Deploy. Open the HTTPS URL Render gives you.

Do not put your API key in frontend code or commit it to GitHub.

## Run locally
Python 3.10+:

```bash
pip install -r requirements.txt
```

Set environment variables before running:

macOS/Linux:
```bash
export GEMINI_API_KEY="your-key"
export GEMINI_MODEL="models/gemini-4-hydrogen"
uvicorn main:app --reload
```

Windows PowerShell:
```powershell
$env:GEMINI_API_KEY="your-key"
$env:GEMINI_MODEL="models/gemini-4-hydrogen"
uvicorn main:app --reload
```

Then visit http://127.0.0.1:8000

## Install on Android
After deploying to HTTPS:
1. Open the website in Chrome on Android.
2. Open the browser menu.
3. Tap "Install app" or "Add to Home screen" (wording may vary).
4. Fidel AI will appear on your home screen.

## APK
This is an installable PWA, not a signed APK. A native Android APK can be
created later by wrapping this deployed HTTPS PWA with an Android packaging
tool such as Bubblewrap or Capacitor. Publishing/signing requires an Android
package name and signing key, which must be controlled by the app owner.

## Notes
- The default Gemini model ID is inherited from your original script. It may
  need changing if your API account does not have access to it.
- Voice capture and PWA installation require HTTPS in deployment.
- Browser localStorage is device/browser-specific; it is not cross-device cloud
  memory. Do not store passwords or sensitive personal information.
- The backend logs technical exceptions to the hosting service logs and sends
  a generic error to the browser.
