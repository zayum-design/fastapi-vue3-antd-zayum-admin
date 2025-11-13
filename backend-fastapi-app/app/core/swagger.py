"""
Swagger UI 配置和模板模块
"""
from app.core.config import settings


def get_swagger_html_template():
    """获取 Swagger UI HTML 模板"""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>{settings.PROJECT_NAME} - API Documentation</title>
    <link rel="stylesheet" type="text/css" href="{settings.SWAGGER_CSS_URL}" />
    <link rel="shortcut icon" href="{settings.SWAGGER_FAVICON_URL}" />
    <style>
        html {{
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }}
        *,
        *:before,
        *:after {{
            box-sizing: inherit;
        }}
        body {{
            margin: 0;
            background: #fafafa;
        }}
        .loading {{
            text-align: center;
            padding: 50px;
            font-family: Arial, sans-serif;
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <div id="loading" class="loading">{settings.SWAGGER_LOADING_TEXT}</div>
    
    <script>
        // 多重 CDN 备用方案
        const loadScript = (url, onSuccess, onError) => {{
            const script = document.createElement('script');
            script.src = url;
            script.onload = onSuccess;
            script.onerror = onError;
            document.head.appendChild(script);
        }};

        const loadSwaggerUI = () => {{
            const config = {{
                url: '{settings.API_ADMIN_STR}/openapi.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "BaseLayout",
                showExtensions: true,
                showCommonExtensions: true
            }};

            const ui = SwaggerUIBundle(config);
            window.ui = ui;
            document.getElementById('loading').style.display = 'none';
        }};

        const tryLoadSwagger = () => {{
            // 尝试加载 Swagger UI 资源
            loadScript(
                '{settings.SWAGGER_BUNDLE_JS_URLS[0]}',
                () => {{
                    // 成功加载 bundle，现在加载 preset
                    loadScript(
                        '{settings.SWAGGER_PRESET_JS_URLS[0]}',
                        () => {{
                            loadSwaggerUI();
                        }},
                        () => {{
                            // 如果 preset 加载失败，尝试备用 CDN
                            loadScript(
                                '{settings.SWAGGER_PRESET_JS_URLS[1]}',
                                () => {{
                                    loadSwaggerUI();
                                }},
                                () => {{
                                    document.getElementById('loading').innerHTML = 
                                        '{settings.SWAGGER_ERROR_MESSAGE}: <a href="{settings.API_ADMIN_STR}/openapi.json" target="_blank">{settings.API_ADMIN_STR}/openapi.json</a>';
                                }}
                            );
                        }}
                    );
                }},
                () => {{
                    // 如果 bundle 加载失败，尝试备用 CDN
                    loadScript(
                        '{settings.SWAGGER_BUNDLE_JS_URLS[1]}',
                        () => {{
                            loadScript(
                                '{settings.SWAGGER_PRESET_JS_URLS[1]}',
                                () => {{
                                    loadSwaggerUI();
                                }},
                                () => {{
                                    document.getElementById('loading').innerHTML = 
                                        '{settings.SWAGGER_ERROR_MESSAGE}: <a href="{settings.API_ADMIN_STR}/openapi.json" target="_blank">{settings.API_ADMIN_STR}/openapi.json</a>';
                                }}
                            );
                        }},
                        () => {{
                            document.getElementById('loading').innerHTML = 
                                '{settings.SWAGGER_ERROR_MESSAGE}: <a href="{settings.API_ADMIN_STR}/openapi.json" target="_blank">{settings.API_ADMIN_STR}/openapi.json</a>';
                        }}
                    );
                }}
            );
        }};

        window.onload = tryLoadSwagger;
    </script>
</body>
</html>
"""


def get_custom_swagger_ui():
    """获取自定义 Swagger UI 页面内容"""
    return get_swagger_html_template()
