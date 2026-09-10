module.exports = {
  requires: {
    bundle: "ai"
  },
  run: [
    {
      method: "script.start",
      params: {
        uri: "torch.js",
        params: {
          venv: "env",
          path: "app"
        }
      }
    },
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        message: [
          "uv pip install -r requirements.txt",
          "uv pip check"
        ]
      }
    },
    {
      method: "notify",
      params: {
        html: "Installation complete! Click 'Start' to launch Hy-MT2. Models will be downloaded automatically from Hugging Face on first use."
      }
    }
  ]
}
