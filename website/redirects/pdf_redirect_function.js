function handler(event) {
          var request = event.request;
          if (request.uri.startsWith('/files/')) {
            request.uri = request.uri.slice(6);
          }

          var uri = request.uri;
          // Exact path redirects
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
            "/documents/Rule-151_1_Amended_03202023.pdf": "/files/documents/rule-151.1.pdf",
          };

          if (redirects[uri]) {
            return {
              statusCode: 302,
              statusDescription: "Found",
              headers: {
                location: { value: redirects[uri].replace("/documents/Rule-", "/documents/rule-") }
              }
            };
          }
          // Regex-based fallback logic
          var pattern = /^\/documents\/Rule-\d+[.\-_A-Za-z0-9]*?(amended|Amended|superseded|2nd|2nd-amended|New|new)[^\/]*\.pdf$/;
          var genericPattern = /^\/documents\/Rule-[\d.]+\.pdf$/;

          if (pattern.test(uri)) {
            var newUri = uri.replace(/^\/documents\/(Rule-\d+)[^\/]*\.pdf$/, "/documents/$1.pdf");
            newUri = newUri.replace("/documents/Rule-", "/documents/rule-"); // lowercase only "Rule"
            return {
              statusCode: 302,
              statusDescription: "Found",
              headers: {
                location: { value: "/files" + newUri }
              }
            };
          }

          if (genericPattern.test(uri)) {
            var newUri = uri.replace("/documents/Rule-", "/documents/rule-"); // lowercase only "Rule"
            return {
              statusCode: 302,
              statusDescription: "Found",
              headers: {
                location: { value: "/files" + newUri }
              }
            };
          }
          return request;
        }
