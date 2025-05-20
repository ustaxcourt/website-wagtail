const { S3Client, GetObjectCommand } = require("@aws-sdk/client-s3");

const s3Client = new S3Client({});

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
        const stream = response.Body;

        // Convert stream to buffer
        const chunks = [];
        for await (const chunk of stream) {
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

        // Return the response
        return {
            statusCode: 200,
            headers: {
                'Content-Type': contentType,
                'Cache-Control': 'max-age=3600'
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
