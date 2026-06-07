function doGet() {
  return HtmlService.createHtmlOutputFromFile("Index")
    .setTitle("Hello World")
    .addMetaTag("viewport", "width=device-width, initial-scale=1");
}
