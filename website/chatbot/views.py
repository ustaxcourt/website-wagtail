import json
import logging

import boto3
from botocore.exceptions import ClientError
from django.http import JsonResponse
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)

BEDROCK_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"
BEDROCK_REGION = "us-east-1"

SYSTEM_PROMPT = """You are a helpful assistant for the United States Tax Court website.
You help people understand how to file a petition, what to expect during their case,
and how to navigate Tax Court procedures. Answer questions clearly and concisely.
If a question is outside the scope of U.S. Tax Court procedures, politely say so and
redirect the user to the relevant Tax Court resources at ustaxcourt.gov.

Key facts about the U.S. Tax Court:
- The U.S. Tax Court is a federal court where taxpayers can dispute IRS determinations
  before paying the disputed tax.
- To start a case, a taxpayer files a Petition (Form 2 or the Petition Kit) within
  90 days of receiving a Statutory Notice of Deficiency (or 150 days if the notice
  was addressed to someone outside the United States).
- There is a $60 filing fee, which may be waived for low-income taxpayers.
- Cases may be heard in-person at a city near the taxpayer or remotely via Zoomgov.
- The DAWSON system (dawson.ustaxcourt.gov) is the court's electronic filing system.
- Petitioners (taxpayers) can represent themselves or be represented by a
  tax practitioner admitted to practice before the Tax Court.
- Small Tax Cases (S cases) are available for disputes of $50,000 or less per year;
  they are informal and decisions cannot be appealed.
- Regular cases involve larger amounts and follow more formal procedures.
- Free legal help may be available through Low Income Taxpayer Clinics (LITCs)
  or Calendar Call clinics.
- The court's rules of practice and procedure govern all cases.
"""


@require_POST
def ask(request):
    try:
        body = json.loads(request.body)
        user_message = body.get("message", "").strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({"error": "Invalid request body."}, status=400)

    if not user_message:
        return JsonResponse({"error": "Message cannot be empty."}, status=400)

    if len(user_message) > 1000:
        return JsonResponse(
            {"error": "Message is too long (max 1000 characters)."}, status=400
        )

    try:
        client = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
        response = client.converse(
            modelId=BEDROCK_MODEL_ID,
            system=[{"text": SYSTEM_PROMPT}],
            messages=[{"role": "user", "content": [{"text": user_message}]}],
            inferenceConfig={"maxTokens": 512, "temperature": 0.3},
        )
        answer = response["output"]["message"]["content"][0]["text"]
        return JsonResponse({"response": answer})
    except ClientError as e:
        logger.error("Bedrock ClientError: %s", e)
        return JsonResponse(
            {"error": "Could not reach the AI service. Please try again later."},
            status=503,
        )
    except Exception as e:
        logger.error("Unexpected error calling Bedrock: %s", e)
        return JsonResponse({"error": "An unexpected error occurred."}, status=500)
