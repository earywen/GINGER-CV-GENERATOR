module.exports = {
  apps: [
    {
      name: 'burgeap-cv-generator',
      script: 'serve.py',
      cwd: '/home/beelink/projets/burgeap-cv-generator',
      interpreter: '/home/beelink/venv_antigravity_bot/bin/python3',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production',
        PORT: 8085
      }
    }
  ]
};
