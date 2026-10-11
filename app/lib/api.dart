import 'dart:convert';

import 'package:http/http.dart' as http;

class Api {
  // Chrome / Windows desktop: http://127.0.0.1:8000
  // Android emulator:        http://10.0.2.2:8000
  // Physical phone:          http://<your PC's Wi-Fi IP>:8000 (start uvicorn with --host 0.0.0.0)
  static const String baseUrl = 'http://127.0.0.1:8000';

  static const Map<String, String> _headers = {'Content-Type': 'application/json'};

  static Map<String, dynamic> _parse(http.Response res) {
    if (res.statusCode != 200) {
      var msg = 'Server returned ${res.statusCode}';
      try {
        final body = jsonDecode(utf8.decode(res.bodyBytes));
        if (body is Map && body['detail'] is String) {
          msg = body['detail'] as String;
        }
      } catch (_) {}
      throw Exception(msg);
    }
    return jsonDecode(utf8.decode(res.bodyBytes)) as Map<String, dynamic>;
  }

  static Future<Map<String, dynamic>> runGoal(String goal) async {
    final res = await http
        .post(
      Uri.parse('$baseUrl/run'),
      headers: _headers,
      body: jsonEncode({'goal': goal}),
    )
        .timeout(const Duration(minutes: 20));
    return _parse(res);
  }

  static Future<List<dynamic>> listRuns() async {
    final res = await http.get(Uri.parse('$baseUrl/runs?limit=50'));
    return _parse(res)['runs'] as List<dynamic>;
  }

  static Future<Map<String, dynamic>> getRun(int id) async {
    final res = await http.get(Uri.parse('$baseUrl/runs/$id'));
    return _parse(res);
  }

  static Future<List<dynamic>> ingest() async {
    final res = await http.post(Uri.parse('$baseUrl/ingest'));
    return _parse(res)['ingested'] as List<dynamic>;
  }
}