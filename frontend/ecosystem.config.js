module.exports = {
  apps: [
    {
      name: 'hyper-ai-frontend',
      script: 'npm',
      args: 'start',
      cwd: '/var/www/hypershopcomercio.com.br/hyper-ai/frontend',
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      }
    }
  ]
};
