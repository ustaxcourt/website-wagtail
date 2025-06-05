import boto3
import uuid
import logging

logger = logging.getLogger(__name__)


def invalidate_cloudfront_cache(distribution_id, paths=None):
    """
    Invalidate CloudFront cache for given paths.
    Defaults to full-site invalidation if no paths specified.
    """
    if paths is None:
        paths = ["/*"]  # Conservative default

    try:
        client = boto3.client("cloudfront")
        response = client.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                "Paths": {
                    "Quantity": len(paths),
                    "Items": paths,
                },
                "CallerReference": str(uuid.uuid4()),
            },
        )
        logger.info(f"CloudFront invalidation ID: {response['Invalidation']['Id']}")
        return response
    except Exception as e:
        logger.error(f"CloudFront invalidation failed: {e}")
        raise
