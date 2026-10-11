import 'package:flutter/material.dart';

import '../api.dart';

class DocumentsScreen extends StatefulWidget {
  const DocumentsScreen({super.key});

  @override
  State<DocumentsScreen> createState() => _DocumentsScreenState();
}

class _DocumentsScreenState extends State<DocumentsScreen> {
  bool _busy = false;
  String? _error;
  List<Map<String, dynamic>>? _files;

  Future<void> _ingest() async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final files = await Api.ingest();
      if (!mounted) return;
      setState(() => _files = files.cast<Map<String, dynamic>>());
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = 'Ingest failed: $e');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          'Your notes stay on this computer. Put .md, .txt, .pdf or .docx '
              'files in backend/data/docs, then tap the button so the agents '
              'can search them.',
          style: Theme.of(context).textTheme.bodyMedium,
        ),
        const SizedBox(height: 12),
        FilledButton.icon(
          onPressed: _busy ? null : _ingest,
          icon: const Icon(Icons.sync),
          label: Text(_busy ? 'Reading notes...' : 'Ingest notes'),
        ),
        if (_error != null) ...[
          const SizedBox(height: 12),
          Text(
            _error!,
            style: TextStyle(color: Theme.of(context).colorScheme.error),
          ),
        ],
        if (_files != null) ...[
          const SizedBox(height: 16),
          Text('Indexed files', style: Theme.of(context).textTheme.titleMedium),
          if (_files!.isEmpty)
            const Padding(
              padding: EdgeInsets.only(top: 8),
              child: Text('No supported files found in the folder.'),
            ),
          for (final f in _files!)
            ListTile(
              dense: true,
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.description_outlined),
              title: Text('${f['file']}'),
              subtitle: Text('${f['chunks']} chunks'),
            ),
        ],
      ],
    );
  }
}