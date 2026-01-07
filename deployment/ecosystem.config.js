// PM2 ecosystem configuration for System//Zero
module.exports = {
  apps: [{
    name: 'systemzero-api',
    script: '.venv/bin/uvicorn',
    args: 'systemzero.interface.api.server:app --host 0.0.0.0 --port 8000',
    cwd: '/opt/systemzero',
    instances: 4,
    exec_mode: 'cluster',
    
    // Restart policy
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    min_uptime: '10s',
    max_restarts: 10,
    restart_delay: 4000,
    
    // Environment
    env: {
      NODE_ENV: 'production',
      SYSTEMZERO_ENV: 'production',
      LOG_LEVEL: 'INFO',
      LOG_JSON: 'true',
      PYTHONPATH: '/opt/systemzero'
    },
    
    env_development: {
      NODE_ENV: 'development',
      SYSTEMZERO_ENV: 'development',
      LOG_LEVEL: 'DEBUG',
      LOG_JSON: 'false',
      PYTHONPATH: '/opt/systemzero'
    },
    
    // Logging
    error_file: '/opt/systemzero/logs/pm2-error.log',
    out_file: '/opt/systemzero/logs/pm2-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    
    // Health checks
    listen_timeout: 10000,
    kill_timeout: 5000,
    wait_ready: true,
    
    // Advanced
    instance_var: 'INSTANCE_ID',
    vizion: false,
    post_update: ['pip install -r requirements.txt']
  }]
};
