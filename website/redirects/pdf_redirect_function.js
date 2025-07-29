function handler(event) {
          var request = event.request;
          var uri = request.uri;
          var pattern = /^\/documents\/Rule-\d+[.\-_A-Za-z0-9]*?(amended|Amended|superseded|2nd|2nd-amended|New|new)[^\/]*\.pdf$/;
          var genericPattern = /^\/documents\/Rule-[\d.]+\.pdf$/;

          if (pattern.test(uri)) {
            var newUri = uri.replace(/^\/documents\/(Rule-\d+)[^\/]*\.pdf$/, "/documents/$1.pdf").toLowerCase();
            return {
              statusCode: 302,
              statusDescription: "Found",
              headers: {
                location: { value: newUri }
              }
            };
          }
          if (genericPattern.test(uri)) {
              return {
                statusCode: 302,
                statusDescription: "Found",
                headers: {
                  location: { value: uri.toLowerCase() }
                }
              };
            }
          // Strip /files prefix if present (CloudFront origin routing)
          if (request.uri.startsWith('/files/')) {
            request.uri = request.uri.slice(6);
          }
          return request;
        }
