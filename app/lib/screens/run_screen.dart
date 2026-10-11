import 'dart:async';

import 'package:flutter/material.dart';

import '../api.dart';
import '../widgets/run_result_view.dart';

class RunScreen extends StatefulWidget {
  const RunScreen({super.key});

  @override
  State<RunScreen> createState() => _RunScreenState();
}

class _RunScreenState extends State<RunScreen> {
  final _controller = TextEditingController();
  bool _running = false;
  int _elapsed = 0;
  Timer? _timer;
  String? _error;
  Map<String, dynamic>? _result;

  @override
  void dispose() {
    _timer?.cancel();
    _controller.dispose();
    super.dispose();
  }

  Future<void> _run() async {
    final goal = _controller.text.trim();
    if (goal.isEmpty) {
      setState(() => _error = 'Type a goal first');
      return;
    }
    setState(() {
      _running = true;
      _elapsed = 0;
      _error = null;
      _result = null;
    });
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (mounted) setState(() => _elapsed++);
    });
    try {
      final data = await Api.runGoal(goal);
      if (!mounted) return;
      setState(() => _result = data);
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      _timer?.cancel();
      if (mounted) setState(() => _running = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        TextField(
          controller: _controller,
          minLines: 2,
          maxLines: 4,
          enabled: !_running,
          decoration: const InputDecoration(
            border: OutlineInputBorder(),
            labelText: 'Your goal',
            hintText: 'e.g. Prepare me for my DBMS exam in 2 weeks',
          ),
        ),
        const SizedBox(height: 12),
        FilledButton.icon(
          onPressed: _running ? null : _run,
          icon: const Icon(Icons.play_arrow),
          label: const Text('Run'),
        ),
        if (_running) ...[
          const SizedBox(height: 16),
          Row(
            children: [
              const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
              const SizedBox(width: 12),
              Text('Agents are working...  ${_elapsed}s'),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            'This usually takes 2 to 3 minutes on the local model.',
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
        if (_error != null) ...[
          const SizedBox(height: 12),
          Text(
            _error!,
            style: TextStyle(color: Theme.of(context).colorScheme.error),
          ),
        ],
        if (_result != null) ...[
          const Divider(height: 32),
          if (_result!['mode'] == 'chat')
            Card(
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SelectableText('${_result!['reply']}'),
                    if ((_result!['sources'] as List).isNotEmpty) ...[
                      const SizedBox(height: 8),
                      Text(
                        'Sources: ${(_result!['sources'] as List).join(', ')}',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ],
                ),
              ),
            )
          else
            RunResultView(data: _result!),
        ],
      ],
    );
  }
}