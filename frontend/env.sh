#!/bin/sh
# Replace environment variables in the main.js file at runtime

# Find all .js files in the /usr/share/nginx/html directory and its subdirectories
JS_FILES=$(find /usr/share/nginx/html -type f -name "*.js")

# Replace environment variables
for file in $JS_FILES; do
  # Replace __VITE_API_URL__ with VITE_API_URL environment variable
  sed -i 's|__VITE_API_URL__|'${VITE_API_URL:-http://localhost:8000}'|g' $file
done

# Continue with the normal Nginx startup process
exec "$@"
