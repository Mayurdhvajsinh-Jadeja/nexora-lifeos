import 'package:flutter/material.dart';

import '../api.dart';
import '../widgets/run_result_view.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  late Future<List<dynamic>> _future;

  @override
  void initState() {
    super.initState();
    _future = Api.listRuns();
  }

  void _reload() => setState(() => _future = Api.listRuns());

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<dynamic>>(
      future: _future,
      builder: (context, snap) {
        if (snap.connectionState != ConnectionState.done) {
          return const Center(child: CircularProgressIndicator());
        }
        if (snap.hasError) {
          return Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text('Could not load history: ${snap.error}'),
                const SizedBox(height: 12),
                FilledButton(onPressed: _reload, child: const Text('Retry')),
              ],
            ),
          );
        }
        final runs = snap.data!.cast<Map<String, dynamic>>();
        if (runs.isEmpty) {
          return const Center(child: Text('No runs yet. Run a goal first.'));
        }
        return RefreshIndicator(
          onRefresh: () async => _reload(),
          child: ListView.separated(
            itemCount: runs.length,
            separatorBuilder: (_, __) => const Divider(height: 1),
            itemBuilder: (context, i) {
              final r = runs[i];
              return ListTile(
                title: Text('${r['goal']}'),
                subtitle: Text(
                  'Run #${r['id']}  |  ${r['total_seconds']}s  |  '
                      'retries ${r['retries']}  |  ${r['final_verdict']}',
                ),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) => RunDetailScreen(runId: r['id'] as int),
                  ),
                ),
              );
            },
          ),
        );
      },
    );
  }
}

class RunDetailScreen extends StatelessWidget {
  final int runId;

  const RunDetailScreen({super.key, required this.runId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Run #$runId')),
      body: FutureBuilder<Map<String, dynamic>>(
        future: Api.getRun(runId),
        builder: (context, snap) {
          if (snap.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snap.hasError) {
            return Center(child: Text('Could not load run: ${snap.error}'));
          }
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Text(
                '${snap.data!['goal']}',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 12),
              RunResultView(data: snap.data!),
            ],
          );
        },
      ),
    );
  }
}