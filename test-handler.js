const axios = require('axios');

const RUNPOD_ENDPOINT = 'https://api.runpod.ai/v2/7jif0u23zst5r9/run';
const API_KEY = process.env.RUNPOD_API_KEY || 'your_api_key_here';

// Simple Social Twin workflow for testing
const socialTwinWorkflow = {
    "6": {
        "inputs": {
            "text": "professional headshot portrait of a confident business person, studio lighting, clean background, high quality, detailed",
            "clip": ["30", 1]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {
            "title": "CLIP Text Encode (Positive Prompt)"
        }
    },
    "8": {
        "inputs": {
            "samples": ["31", 0],
            "vae": ["30", 2]
        },
        "class_type": "VAEDecode",
        "_meta": {
            "title": "VAE Decode"
        }
    },
    "9": {
        "inputs": {
            "filename_prefix": "social_twin_test",
            "images": ["8", 0]
        },
        "class_type": "SaveImage",
        "_meta": {
            "title": "Save Image"
        }
    },
    "30": {
        "inputs": {
            "ckpt_name": "flux1-dev.safetensors"
        },
        "class_type": "CheckpointLoaderSimple",
        "_meta": {
            "title": "Load Checkpoint"
        }
    },
    "31": {
        "inputs": {
            "seed": 42,
            "steps": 20,
            "cfg": 1.0,
            "sampler_name": "euler",
            "scheduler": "simple",
            "denoise": 1.0,
            "model": ["30", 0],
            "positive": ["6", 0],
            "negative": ["32", 0],
            "latent_image": ["33", 0]
        },
        "class_type": "KSampler",
        "_meta": {
            "title": "KSampler"
        }
    },
    "32": {
        "inputs": {
            "text": "blurry, low quality, distorted, amateur",
            "clip": ["30", 1]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {
            "title": "CLIP Text Encode (Negative Prompt)"
        }
    },
    "33": {
        "inputs": {
            "width": 1024,
            "height": 1024,
            "batch_size": 1
        },
        "class_type": "EmptyLatentImage",
        "_meta": {
            "title": "Empty Latent Image"
        }
    }
};

async function testFixedHandler() {
    try {
        console.log('🚀 Testing FIXED RunPod handler with Social Twin workflow...');
        
        const response = await axios.post(RUNPOD_ENDPOINT, {
            input: {
                workflow: socialTwinWorkflow
            }
        }, {
            headers: {
                'Authorization': `Bearer ${API_KEY}`,
                'Content-Type': 'application/json'
            },
            timeout: 30000
        });

        console.log('📦 Job submitted successfully!');
        console.log('📋 Job ID:', response.data.id);
        console.log('📊 Status:', response.data.status);

        if (response.data.id) {
            console.log('⏳ Monitoring job progress...');
            await monitorJob(response.data.id);
        }

    } catch (error) {
        console.error('❌ Error:', error.message);
        if (error.response) {
            console.error('📄 Response data:', JSON.stringify(error.response.data, null, 2));
            console.error('📊 Status:', error.response.status);
        }
    }
}

async function monitorJob(jobId) {
    const maxAttempts = 40; // 10 minutes with 15-second intervals
    
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        try {
            await new Promise(resolve => setTimeout(resolve, 15000)); // Wait 15 seconds
            
            const statusResponse = await axios.get(`https://api.runpod.ai/v2/7jif0u23zst5r9/status/${jobId}`, {
                headers: {
                    'Authorization': `Bearer ${API_KEY}`
                }
            });

            const status = statusResponse.data.status;
            console.log(`🔍 Check ${attempt}/${maxAttempts} - Status: ${status}`);

            if (status === 'COMPLETED') {
                console.log('✅ Job completed successfully!');
                console.log('📄 Output:', JSON.stringify(statusResponse.data.output, null, 2));
                
                if (statusResponse.data.output && statusResponse.data.output.images) {
                    console.log(`🖼️ Generated ${statusResponse.data.output.images.length} image(s)`);
                }
                
                break;
            } else if (status === 'FAILED') {
                console.log('❌ Job failed!');
                console.log('📄 Error details:', JSON.stringify(statusResponse.data, null, 2));
                break;
            } else if (status === 'IN_QUEUE') {
                console.log('⏳ Job still in queue...');
            } else if (status === 'IN_PROGRESS') {
                console.log('🔄 Job in progress...');
            } else {
                console.log(`⚠️ Unexpected status: ${status}`);
                console.log('📄 Full response:', JSON.stringify(statusResponse.data, null, 2));
            }

        } catch (error) {
            console.error(`❌ Error checking status (attempt ${attempt}):`, error.message);
        }
    }
}

// Run the test
testFixedHandler();
