export default {
  async fetch(request) {
    const url = new URL(request.url);

    if (url.pathname === "/api/health") {
      return Response.json({
        status: "ok",
        service: "project-invent-ai-reviewer",
        mock: true,
      });
    }

    if (url.pathname === "/api/evaluate") {
      return Response.json({
        status: "ok",
        mock: true,
        fileName: "sample-upload.txt",
        review: {
          summary: "Mock review: the document looks structurally sound and ready for a first pass.",
          score: 82,
          highlights: [
            "The upload was received successfully.",
            "The content starts with a clear opening paragraph."
          ],
          nextSteps: [
            "Add clearer section headings.",
            "Check spelling and formatting."
          ]
        }
      });
    }

    return new Response("Not Found", { status: 404 });
  }
};
