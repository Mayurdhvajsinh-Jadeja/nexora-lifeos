import 'package:flutter/material.dart';

class RunResultView extends StatelessWidget {
  final Map<String, dynamic> data;

  const RunResultView({super.key, required this.data});

  Widget _title(BuildContext context, String text) => Padding(
    padding: const EdgeInsets.only(top: 20, bottom: 8),
    child: Text(text, style: Theme.of(context).textTheme.titleMedium),
  );

  @override
  Widget build(BuildContext context) {
    final plan = data['plan'] as Map<String, dynamic>;
    final planTasks = (plan['tasks'] as List).cast<Map<String, dynamic>>();
    final tasks =
    ((data['tasks'] ?? data['log']) as List).cast<Map<String, dynamic>>();
    final reviews = (data['reviews'] as List).cast<Map<String, dynamic>>();
    final finalAnswer = (data['final_answer'] ?? '') as String;

    final verdict = reviews.isEmpty ? '-' : reviews.last['verdict'] as String;
    final retries = tasks.where((t) => (t['attempt'] as int) > 1).length;
    var seconds = 0.0;
    for (final t in tasks) {
      seconds += (t['seconds'] as num).toDouble();
    }
    for (final r in reviews) {
      seconds += (r['seconds'] as num).toDouble();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Wrap(
          spacing: 8,
          runSpacing: 4,
          children: [
            Chip(
              avatar: Icon(
                verdict == 'PASS' ? Icons.check_circle : Icons.error_outline,
                size: 18,
              ),
              label: Text('Review: $verdict'),
            ),
            Chip(label: Text('Retries: $retries')),
            Chip(label: Text('Compute: ${seconds.toStringAsFixed(0)}s')),
          ],
        ),
        _title(context, 'Final answer'),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: SelectableText(finalAnswer),
          ),
        ),
        _title(context, 'Plan'),
        for (final t in planTasks)
          ListTile(
            dense: true,
            contentPadding: EdgeInsets.zero,
            leading: CircleAvatar(radius: 12, child: Text('${t['id']}')),
            title: Text('${t['title']}'),
            subtitle: Text(
              '${t['agent']}'
                  '${(t['depends_on'] as List).isEmpty ? '' : '  |  after ${(t['depends_on'] as List).join(', ')}'}',
            ),
          ),
        _title(context, 'Task details'),
        for (final t in tasks)
          ExpansionTile(
            tilePadding: EdgeInsets.zero,
            title: Text('${t['title']}'),
            subtitle: Text(
              '${t['agent']}  |  ${t['seconds']}s  |  attempt ${t['attempt']}'
                  '${t['truncated'] == true ? '  |  cut off' : ''}',
            ),
            children: [
              Align(
                alignment: Alignment.centerLeft,
                child: Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: SelectableText('${t['output']}'),
                ),
              ),
              if ((t['sources'] as List).isNotEmpty)
                Align(
                  alignment: Alignment.centerLeft,
                  child: Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: Text(
                      'Sources: ${(t['sources'] as List).join(', ')}',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ),
                ),
            ],
          ),
        _title(context, 'Reviews'),
        for (var i = 0; i < reviews.length; i++)
          ListTile(
            dense: true,
            contentPadding: EdgeInsets.zero,
            title: Text(
                '${reviews[i]['kind'] == 'rules' ? 'Rule check' : 'AI review'}: ${reviews[i]['verdict']}  (${reviews[i]['seconds']}s)'),
            subtitle: (reviews[i]['issues'] as List).isEmpty
                ? const Text('No issues')
                : Text((reviews[i]['issues'] as List)
                .map((x) => 'Task ${x['task_id']}: ${x['problem']}')
                .join('\n')),
          ),
      ],
    );
  }
}