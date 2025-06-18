import logging
import traceback


class JSONExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("django.request")

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        """
        Process exceptions and log them as JSON
        """
        trace = traceback.format_exc()
        self.logger.error(
            "Unhandled exception",
            extra={
                "path": request.path,
                "method": request.method,
                "exception": str(exception),
                "traceback": trace,
            },
        )

        # Let Django handle the response normally
        return None


class NoCacheForLoggedInUsersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            response[
                "Cache-Control"
            ] = "private, no-store, no-cache, must-revalidate, max-age=0"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            response["X-Logged-In-User"] = "true"
        else:
            response["Cache-Control"] = "max-age=300"
        return response


class ForceSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Force session creation for OAuth requests
        if "/login/azuread-tenant-oauth2/" in request.path:
            if not request.session.session_key:
                request.session.create()
                request.session.save()

        response = self.get_response(request)
        return response


class DebugSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("django.request")

    def __call__(self, request):
        # Log session info for all OAuth-related requests
        if any(
            path in request.path
            for path in [
                "/login/azuread-tenant-oauth2/",
                "/complete/azuread-tenant-oauth2/",
            ]
        ):
            self.logger.info(f"=== OAuth Debug for {request.path} ===")
            self.logger.info(
                f"Session key: {getattr(request.session, 'session_key', 'None')}"
            )
            self.logger.info(f"Session exists: {hasattr(request, 'session')}")
            self.logger.info(
                f"Session modified: {getattr(request.session, 'modified', 'Unknown')}"
            )
            self.logger.info(
                f"Session accessed: {getattr(request.session, 'accessed', 'Unknown')}"
            )

            if hasattr(request, "session"):
                self.logger.info(f"Session items: {dict(request.session)}")
                self.logger.info(
                    f"Session cycle key: {getattr(request.session, 'cycle_key', 'None')}"
                )

            self.logger.info(f"Request method: {request.method}")
            self.logger.info(f"GET params: {dict(request.GET)}")
            self.logger.info(f"Cookies: {request.COOKIES}")

            # Check for sessionid cookie specifically
            session_cookie = request.COOKIES.get("sessionid")
            self.logger.info(f"Session cookie value: {session_cookie}")

        response = self.get_response(request)

        # Log session info after processing
        if any(
            path in request.path
            for path in [
                "/login/azuread-tenant-oauth2/",
                "/complete/azuread-tenant-oauth2/",
            ]
        ):
            self.logger.info(f"=== After processing {request.path} ===")
            if hasattr(request, "session"):
                self.logger.info(f"Final session items: {dict(request.session)}")
                self.logger.info(f"Session was modified: {request.session.modified}")

        return response
