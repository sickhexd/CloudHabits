<?php
/**
 * PHP Proxy для Python FastAPI приложения
 * Этот файл проксирует все запросы к Python приложению, работающему на localhost:5000
 */

// URL вашего Python приложения
$python_app_url = 'http://127.0.0.1:5000';

// Получаем путь запроса и query string из REQUEST_URI
// REQUEST_URI содержит полный путь с query string (если есть)
$request_uri = $_SERVER['REQUEST_URI'] ?? '/';

// Парсим URI для получения пути и query string
$parsed_uri = parse_url($request_uri);
$request_path = $parsed_uri['path'] ?? '/';

// Получаем query string из parsed URI или из QUERY_STRING
$query_string = '';
if (isset($parsed_uri['query']) && !empty($parsed_uri['query'])) {
    $query_string = '?' . $parsed_uri['query'];
} elseif (isset($_SERVER['QUERY_STRING']) && !empty($_SERVER['QUERY_STRING'])) {
    $query_string = '?' . $_SERVER['QUERY_STRING'];
}

// Формируем полный URL для запроса к Python приложению
$target_url = $python_app_url . $request_path . $query_string;

// Получаем метод запроса
$method = $_SERVER['REQUEST_METHOD'];

// Инициализируем cURL
$ch = curl_init($target_url);

// Собираем заголовки для передачи
$forward_headers = [];

// Важные заголовки для HTMX
$important_headers = [
    'HX-Request', 'HX-Trigger', 'HX-Trigger-Name', 'HX-Target', 'HX-Current-URL',
    'HX-Prompt', 'HX-Boosted', 'HX-History-Restore-Request'
];

// Получаем все заголовки
$all_headers = [];
if (function_exists('getallheaders')) {
    $all_headers = getallheaders();
} else {
    // Fallback для серверов без getallheaders()
    foreach ($_SERVER as $key => $value) {
        if (strpos($key, 'HTTP_') === 0) {
            $header_name = str_replace(' ', '-', ucwords(str_replace('_', ' ', strtolower(substr($key, 5)))));
            $all_headers[$header_name] = $value;
        }
    }
}

foreach ($all_headers as $name => $value) {
    $name_lower = strtolower($name);
    // Передаем HTMX заголовки и другие важные заголовки
    if (in_array($name, $important_headers) || 
        strpos($name_lower, 'hx-') === 0 ||
        in_array($name_lower, ['accept', 'user-agent'])) {
        $forward_headers[] = "$name: $value";
    }
}

// Добавляем стандартные заголовки
$forward_headers[] = 'X-Real-IP: ' . ($_SERVER['REMOTE_ADDR'] ?? '');
$forward_headers[] = 'X-Forwarded-For: ' . ($_SERVER['HTTP_X_FORWARDED_FOR'] ?? $_SERVER['REMOTE_ADDR'] ?? '');
$forward_headers[] = 'X-Forwarded-Proto: ' . (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http');

// Настройки cURL
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_FOLLOWLOCATION => true,
    CURLOPT_HEADER => true,
    CURLOPT_TIMEOUT => 30,
    CURLOPT_CONNECTTIMEOUT => 10,
]);

// Обработка POST/PUT/DELETE запросов
if (in_array($method, ['POST', 'PUT', 'DELETE', 'PATCH'])) {
    // Для POST используем стандартный метод, для остальных - CUSTOMREQUEST
    if ($method !== 'POST') {
        curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
    } else {
        curl_setopt($ch, CURLOPT_POST, true);
    }
    
    // Получаем Content-Type из заголовков
    $content_type = '';
    foreach ($all_headers as $name => $value) {
        if (strtolower($name) === 'content-type') {
            $content_type = strtolower($value);
            break;
        }
    }
    
    // Читаем raw input
    $raw_input = file_get_contents('php://input');
    
    // Для POST запросов
    if ($method === 'POST') {
        $post_data = null;
        $final_content_type = '';
        
        // Приоритет 1: Если есть данные в $_POST (PHP уже распарсил multipart/form-data)
        if (!empty($_POST)) {
            $post_data = http_build_query($_POST);
            $final_content_type = 'application/x-www-form-urlencoded';
        }
        // Приоритет 2: Если есть raw input
        elseif (!empty($raw_input)) {
            // Проверяем, выглядит ли это как form data (содержит = и &)
            $looks_like_form_data = (strpos($raw_input, '=') !== false && strpos($raw_input, '&') !== false);
            
            // Проверяем Content-Type
            if (strpos($content_type, 'application/x-www-form-urlencoded') !== false || 
                (empty($content_type) && $looks_like_form_data)) {
                // Для application/x-www-form-urlencoded данные уже в правильном формате
                // Передаем их как есть без парсинга, чтобы сохранить оригинальный формат
                $post_data = $raw_input;
                $final_content_type = 'application/x-www-form-urlencoded';
            }
            // Если multipart/form-data, PHP уже должен был распарсить в $_POST
            elseif (strpos($content_type, 'multipart/form-data') !== false) {
                // PHP уже должен был распарсить, но если нет - пробуем вручную
                // Для multipart нужно использовать специальную обработку
                // Но обычно PHP уже делает это автоматически
                if (!empty($_POST)) {
                    $post_data = http_build_query($_POST);
                    $final_content_type = 'application/x-www-form-urlencoded';
                } else {
                    // Если не удалось распарсить, отправляем как есть
                    $post_data = $raw_input;
                    $final_content_type = $content_type;
                }
            }
            // Если Content-Type не указан или другой, пробуем распарсить как form data
            else {
                // Если данные выглядят как form data, обрабатываем их как таковые
                if ($looks_like_form_data) {
                    $post_data = $raw_input;
                    $final_content_type = 'application/x-www-form-urlencoded';
                } else {
                    // Пробуем распарсить как application/x-www-form-urlencoded
                    parse_str($raw_input, $parsed_data);
                    if (!empty($parsed_data) && count($parsed_data) > 0) {
                        $post_data = http_build_query($parsed_data);
                        $final_content_type = 'application/x-www-form-urlencoded';
                    } else {
                        // Если не удалось распарсить, но есть знак =, возможно это уже form data
                        if (strpos($raw_input, '=') !== false) {
                            $post_data = $raw_input;
                            $final_content_type = 'application/x-www-form-urlencoded';
                        } else {
                            // Отправляем как есть с оригинальным Content-Type
                            $post_data = $raw_input;
                            $final_content_type = !empty($content_type) ? $content_type : 'application/x-www-form-urlencoded';
                        }
                    }
                }
            }
        }
        
        // Отправляем данные
        if ($post_data !== null && $post_data !== '') {
            // Временное логирование для отладки /completions
            if (strpos($request_path, '/completions') !== false) {
                error_log("[DEBUG /completions] Path: $request_path");
                error_log("[DEBUG /completions] Content-Type: $content_type");
                error_log("[DEBUG /completions] Raw input: " . substr($raw_input, 0, 500));
                error_log("[DEBUG /completions] Post data: " . substr($post_data, 0, 500));
                error_log("[DEBUG /completions] Final Content-Type: $final_content_type");
            }
            
            // Удаляем старый Content-Type и Content-Length если были
            // cURL автоматически установит Content-Length
            $forward_headers = array_filter($forward_headers, function($header) {
                $header_lower = strtolower($header);
                return stripos($header_lower, 'content-type:') === false && 
                       stripos($header_lower, 'content-length:') === false;
            });
            
            // Для application/x-www-form-urlencoded явно устанавливаем Content-Type
            // Это важно для правильной обработки данных формы в FastAPI
            if (strpos($final_content_type, 'application/x-www-form-urlencoded') !== false || 
                empty($final_content_type)) {
                // Явно устанавливаем Content-Type для application/x-www-form-urlencoded
                $forward_headers[] = 'Content-Type: application/x-www-form-urlencoded';
                // Устанавливаем заголовки ПЕРЕД установкой POSTFIELDS
                curl_setopt($ch, CURLOPT_HTTPHEADER, $forward_headers);
                // Передаем данные как строку
                curl_setopt($ch, CURLOPT_POSTFIELDS, $post_data);
            } else {
                // Для других типов контента устанавливаем заголовок вручную
                $forward_headers[] = 'Content-Type: ' . $final_content_type;
                curl_setopt($ch, CURLOPT_HTTPHEADER, $forward_headers);
                curl_setopt($ch, CURLOPT_POSTFIELDS, $post_data);
            }
            
            // Временное логирование заголовков для отладки /completions
            if (strpos($request_path, '/completions') !== false) {
                error_log("[DEBUG /completions] Headers being sent: " . implode(', ', $forward_headers));
                error_log("[DEBUG /completions] Post data length: " . strlen($post_data));
            }
        } elseif ($method === 'POST' && empty($raw_input) && empty($_POST)) {
            // Если нет данных вообще, но это POST - отправляем пустую строку
            curl_setopt($ch, CURLOPT_POSTFIELDS, '');
            $forward_headers = array_filter($forward_headers, function($header) {
                return stripos($header, 'Content-Type:') === false;
            });
            $forward_headers[] = 'Content-Type: application/x-www-form-urlencoded';
        }
    } else {
        // Для PUT, DELETE, PATCH отправляем raw input
        if (!empty($raw_input)) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, $raw_input);
            if (!empty($content_type)) {
                foreach ($all_headers as $name => $value) {
                    if (strtolower($name) === 'content-type') {
                        $forward_headers[] = 'Content-Type: ' . $value;
                        break;
                    }
                }
            }
        }
    }
}

// Устанавливаем заголовки после обработки POST данных
// Но только если они еще не были установлены выше (для POST с данными)
if (!($method === 'POST' && isset($post_data) && $post_data !== null && $post_data !== '')) {
    curl_setopt($ch, CURLOPT_HTTPHEADER, $forward_headers);
}

// Выполняем запрос
$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
$curl_errno = curl_errno($ch);

// Временное логирование для отладки /completions
if (strpos($request_path, '/completions') !== false) {
    error_log("[DEBUG /completions] HTTP Code: $http_code");
    if ($error) {
        error_log("[DEBUG /completions] cURL Error: $error");
    }
    if ($http_code == 422) {
        // Разделяем заголовки и тело для логирования
        $response_parts = explode("\r\n\r\n", $response, 2);
        $response_body = isset($response_parts[1]) ? $response_parts[1] : $response;
        error_log("[DEBUG /completions] Response body: " . substr($response_body, 0, 1000));
    }
}

curl_close($ch);

// Обработка ошибок
if ($curl_errno !== 0 || $error) {
    http_response_code(502);
    $error_msg = "Error connecting to Python application";
    if ($error) {
        $error_msg .= ": $error";
    }
    if ($curl_errno !== 0) {
        $error_msg .= " (cURL error code: $curl_errno)";
    }
    // Для отладки можно добавить информацию о запросе
    if (isset($_GET['debug'])) {
        $error_msg .= "\nTarget URL: $target_url";
        $error_msg .= "\nMethod: $method";
    }
    echo $error_msg;
    exit;
}

// Разделяем заголовки и тело ответа
// Используем explode с лимитом 2, чтобы не разбить тело ответа
$parts = explode("\r\n\r\n", $response, 2);
if (count($parts) < 2) {
    // Если нет разделителя, возможно формат другой или ответ пустой
    $response_body = $response;
} else {
    list($response_headers, $response_body) = $parts;
    
    // Парсим заголовки ответа (если они есть)
    $headers_array = explode("\r\n", $response_headers);
    foreach ($headers_array as $header) {
        if (empty($header)) continue;
        
        // Пропускаем статусную строку (HTTP/1.1 200 OK и т.д.)
        if (strpos($header, 'HTTP/') === 0) continue;
        
        // Пропускаем некоторые заголовки которые могут вызвать конфликты
        $header_lower = strtolower($header);
        if (
            strpos($header_lower, 'transfer-encoding') !== false ||
            strpos($header_lower, 'connection') !== false ||
            strpos($header_lower, 'content-encoding') !== false
        ) {
            continue;
        }
        
        // Отправляем заголовок (важно для HTMX заголовков типа HX-Trigger)
        if (strpos($header, ':') !== false && !headers_sent()) {
            header($header, false);
        }
    }
}

// Устанавливаем HTTP код ответа
http_response_code($http_code);

// Выводим тело ответа
echo $response_body;
