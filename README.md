# AI Software Company

Bu proje, çoklu ajanlı yazılım şirketi fikrini simüle eden başlangıç seviyesinde, çalıştırılabilir bir Python scaffold'ıdır.

Temel bileşenler:
- CEO / Orkestrator
- Researcher
- Architect
- Developer
- QA Reviewer
- Post-Mortem Analyzer
- Self-Updater

Mimari yaklaşım:
- LangGraph benzeri state machine
- CrewAI benzeri rol tabanlı ajanlar
- Docker benzeri sandbox iş akışı
- Tavily / arama API desteği
- hafıza katmanı için Redis / ChromaDB uyumlu tasarım

## Hızlı başlatma

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main "Yeni çıkan X kütüphanesini kullanarak bir e-ticaret botu yaz"
```

## Proje yapısı

```text
app/
  __init__.py
  agents.py
  config.py
  graph.py
  tasks.py
  tools.py
  sandbox.py
  memory.py
  main.py
Dockerfile
docker-compose.yml
requirements.txt
README.md
.env.example
```

## Çalışma akışı

1. CEO task alır
2. Researcher arama yapar ve özet üretir
3. Architect blueprint oluşturur
4. Developer dosyaları üretir
5. QA sandbox içinde çalıştırır
6. Hata varsa geri bildirim döner
7. Başarılıysa yayın ve sonrası için post-mortem yapılır

## Notlar

Bu uygulama üretim ortamı için tam bir AI yazılım şirketi değil; ama çoklu ajanlı Mimari, workflow, sandbox ve ajan tasarımı için temel, çalıştırılabilir bir başlangıç noktasıdır.

Gelecekte eklenmesi önerilenler:
- Ollama + Llama 3 / CodeLlama
- Tavily veya Serper gerçek arama API
- Redis ve ChromaDB hafıza katmanı
- GitHub API ile release flow
- Docker sandbox güvenlik ve timeout ayarları

## Lisans

MIT
