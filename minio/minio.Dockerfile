FROM minio/minio:RELEASE.2025-09-07T16-13-09Z-cpuv1

RUN mc alias set minio1 http://localhost:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}

RUN mc mb minio1/images

RUN mc policy set public minio1/images




