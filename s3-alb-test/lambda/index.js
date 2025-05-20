const { S3Client, GetObjectCommand } = require("@aws-sdk/client-s3");
const { getSignedUrl } = require("@aws-sdk/s3-request-presigner");

const s3Client = new S3Client({});
const MAX_DIRECT_SIZE = 5 * 1024 * 1024; // 5MB

exports.handler = async (event) => {
    try {
        // Get the path from the request
        const path = event.path || '/';
        const key = path === '/' ? 'index.html' : path.substring(1);


        // Get the object from S3
        const command = new GetObjectCommand({
            Bucket: process.env.BUCKET_NAME,
            Key: key
        });

        const response = await s3Client.send(command);
        const contentLength = response.ContentLength || 0;

        // For PDFs and large files, always use pre-signed URLs
        if (key.endsWith('.pdf') || contentLength > MAX_DIRECT_SIZE) {
            const signedUrl = await getSignedUrl(s3Client, command, { expiresIn: 3600 });
            return {
                statusCode: 302,
                headers: {
                    'Location': signedUrl,
                    'Cache-Control': 'max-age=3600'
                }
            };
        }

        // For smaller files, proceed with direct delivery
        const chunks = [];
        for await (const chunk of response.Body) {
            chunks.push(chunk);
        }
        const buffer = Buffer.concat(chunks);

        // Determine content type
        let contentType = 'text/plain';
        if (key.endsWith('.html')) contentType = 'text/html';
        else if (key.endsWith('.css')) contentType = 'text/css';
        else if (key.endsWith('.js')) contentType = 'application/javascript';
        else if (key.endsWith('.png')) contentType = 'image/png';
        else if (key.endsWith('.jpg') || key.endsWith('.jpeg')) contentType = 'image/jpeg';
        else if (key.endsWith('.gif')) contentType = 'image/gif';
        else if (key.endsWith('.svg')) contentType = 'image/svg+xml';
        else if (key.endsWith('.ico')) contentType = 'image/x-icon';
        else if (key.endsWith('.json')) contentType = 'application/json';
        else if (key.endsWith('.txt')) contentType = 'text/plain';
        else if (key.endsWith('.xml')) contentType = 'application/xml';
        else if (key.endsWith('.webp')) contentType = 'image/webp';
        else if (key.endsWith('.woff')) contentType = 'font/woff';
        else if (key.endsWith('.woff2')) contentType = 'font/woff2';
        else if (key.endsWith('.ttf')) contentType = 'font/ttf';
        else if (key.endsWith('.eot')) contentType = 'font/eot';
        else if (key.endsWith('.otf')) contentType = 'font/otf';
        else if (key.endsWith('.ttf')) contentType = 'font/ttf';
        else if (key.endsWith('.pdf')) contentType = 'application/pdf';
        else if (key.endsWith('.docx')) contentType = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
        else if (key.endsWith('.doc')) contentType = 'application/msword';
        else if (key.endsWith('.xls')) contentType = 'application/vnd.ms-excel';
        else if (key.endsWith('.xlsx')) contentType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
        else if (key.endsWith('.pptx')) contentType = 'application/vnd.openxmlformats-officedocument.presentationml.presentation';

        // Return the response
        return {
            statusCode: 200,
            headers: {
                'Content-Type': contentType,
                'Cache-Control': 'max-age=3600',
                'Content-Length': buffer.length.toString()
            },
            body: buffer.toString('base64'),
            isBase64Encoded: true
        };
    } catch (error) {
        console.error('Error:', error);

        // If the object doesn't exist, return 404
        if (error.name === 'NoSuchKey') {
            return {
                statusCode: 404,
                body: 'Not Found'
            };
        }

        // For other errors, return 500
        return {
            statusCode: 500,
            body: 'Internal Server Error'
        };
    }
};
