
        function handler(event) {
          var request = event.request;

          // Strip /files prefix for uniform matching
          var originalUri = request.uri;
          if (request.uri.startsWith("/files/")) {
            request.uri = request.uri.slice(6);
          }

          var uri = request.uri;

          // Exact path redirects (manual override)
          var redirects = {
            "/documents/Complete_Rules_of_Practice_and_Procedure_Amended_080824.pdf": "/files/documents/Complete-Rules-of-Practice-and-Procedure.pdf",
            "/documents/Rule-229A.pdf": "/files/documents/rule-229A.pdf",
            "/documents/Rule-2302nd-amended.pdf": "/files/documents/rule-230.pdf",
            "/documents/Rule-255.1_amended_08082024.pdf": "/files/documents/rule-255.1.pdf",
            "/documents/Rule-255.2New.pdf": "/files/documents/rule-255.2.pdf",
            "/documents/Rule-255.3New.pdf": "/files/documents/rule-255.3.pdf",
            "/documents/Rule-255.4New.pdf": "/files/documents/rule-255.4.pdf",
            "/documents/Rule-255.5New.pdf": "/files/documents/rule-255.5.pdf",
            "/documents/Rule-255.6New.pdf": "/files/documents/rule-255.6.pdf",
            "/documents/Rule-255.7New.pdf": "/files/documents/rule-255.7.pdf",
            "/documents/Rule-151_1_Amended_03202023.pdf": "/files/documents/rule-151.1.pdf"
          };

          // Avoid infinite redirects if already pointing to final URL
          if (originalUri === redirects[uri]) {
            return request;
          }

          if (redirects[uri] && ("/files" + uri) !== redirects[uri]) {
            return {
              statusCode: 301,
              statusDescription: "Permanent Redirect",
              headers: {
                location: { value: redirects[uri] }
              }
            };
          }

          // Early exit ONLY if the URI is already clean and lowercase
          if (/^\/documents\/rule-[a-z0-9.-]+\.pdf$/.test(uri)) {
            return request;
          }

          // Regex fallback for legacy filenames
          var pattern = /^\/documents\/(Rule-[\dA-Za-z.]+)(?:_?Amended.*|_?amended.*|-?superseded|-?2nd-amended|-?New|-?Oct.*|\.\.)?\.pdf$/i;
          var match = uri.match(pattern);

          if (match) {
            var ruleName = match[1];

            // Normalize name
            ruleName = ruleName.replace(/_/g, "-");
            ruleName = ruleName.replace(/(\d)-(\d[A-Z.]?)/g, "$1.$2");
            ruleName = ruleName.replace(/^Rule/i, "rule");

            var newUri = "/files/documents/" + ruleName + ".pdf";

            // Avoid redirecting to self
            if (originalUri !== newUri) {
              return {
                statusCode: 301,
                statusDescription: "Permanent Redirect",
                headers: {
                  location: { value: newUri }
                }
              };
            }
          }

          return request;
        }
