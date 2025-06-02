
/****
 * PDF and link handlers which are used to track links and PDFs and open them in new tabs
 */
function setupLinkHandlers() {
    // Use event delegation instead of querySelectorAll
    document.addEventListener('click', function(event) {
        const link = event.target.closest('a');
        if (!link) return;

        const href = link.getAttribute('href');
        if (!href) return;

        // For same-domain PDFs, let GA track first
        if (isSamedomain(href) && isPdf(href)) {
            window.open(href, '_blank');
            event.preventDefault();
            return;
        }

        if (href.startsWith('mailto:') || href.startsWith('tel:') || isSamedomain(href)) {
            return; // Let default behavior and GA handle these
        }

        // Handle external links
        event.preventDefault();
        if (isSubdomain(href)) {
            window.open(href, '_blank');
        } else {
            const newTab = window.open('/redirect/', '_blank');
            if (newTab) {
                newTab.sessionStorage.setItem('redirect_url', href);
            } else {
                alert('Pop-up blocked! Please allow pop-ups for this site.');
            }
        }
    });
}

function getRootDomain(url) {
    try {
        let hostname = new URL(url, window.location.origin).hostname;
        let parts = hostname.split(".").reverse();

        if (parts.length >= 2) {
            return parts[1] + "." + parts[0]
        }
        return hostname
    } catch (e) {
        return null
    }
}

function isSamedomain(url) {
    let currentDomain = window.location.hostname;
    let s3StaticDomainPattern = /.*ustc-website-assets\.s3\.amazonaws\.com$/;
    let linkDomain;

    try {
        linkDomain = normalize(new URL(url, window.location.origin).hostname);
    } catch (e) {
        return true;
    }

    return (linkDomain === currentDomain || s3StaticDomainPattern.test(linkDomain));
}

function isSubdomain(url) {
    let currentRootDomain = getRootDomain(window.location.hostname);
    let linkRootDomain = getRootDomain(url);

    return linkRootDomain && linkRootDomain === currentRootDomain;
}

function isPdf(url) {
    return url.toLowerCase().endsWith('.pdf')
}

// Queue the setup to run after GA loads
window.gaCallbacks = window.gaCallbacks || [];
window.gaCallbacks.push(setupLinkHandlers);
