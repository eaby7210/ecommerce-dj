
FROM python:3.12-alpine AS builder


ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install build dependencies
RUN apk update && \
    apk add --no-cache postgresql-dev python3-dev build-base && \
    rm -rf /var/cache/apk/*

# Install pipenv and dependencies
RUN pip install --no-cache-dir pipenv

# Copy dependency files
COPY Pipfile Pipfile.lock ./

# Install dependencies into /build
RUN pipenv install --system --deploy --ignore-pipfile

# Final stage
FROM python:3.12-alpine AS backend

# Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=ecommerce.settings.dev \
    DJANGO_PRODUCTION=1

WORKDIR /app

# Install runtime dependencies
RUN apk add --no-cache \
    postgresql-libs \
    libmagic \
    && rm -rf /var/cache/apk/*

# Create app user
RUN addgroup -S django && \
    adduser -S django -G django

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy project files
COPY --chown=django:django . .
RUN chmod 775 /app
RUN chown django:django /app
RUN chown -R django:django /app/db.sqlite3 && chmod 664 /app/db.sqlite3
# Create media and static directories
RUN mkdir -p /app/media /app/static && \
    chown -R django:django /app/media /app/static

# Switch to non-root user
USER django


RUN  chmod +x /app/build.sh

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/build.sh"]
