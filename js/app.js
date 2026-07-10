(function () {
  var homeView = document.getElementById("home-view");
  var readerView = document.getElementById("reader-view");
  var referenceList = document.getElementById("reference-list");
  var readerTitle = document.getElementById("reader-title");
  var pdfFrame = document.getElementById("pdf-frame");
  var btnBack = document.getElementById("btn-back");
  var btnOpenNew = document.getElementById("btn-open-new");

  var activePdf = null;
  var RELEASE_BASE = "https://github.com/123321zzq/h11-papers/releases/download/v1.0.0/";
  var JSDELIVR_BASE = "https://cdn.jsdelivr.net/gh/123321zzq/h11-papers@main/";
  var RELEASE_ONLY = { "01": true, "13": true };

  function resolvePdfUrl(item) {
    var url = item.url;
    if (url.indexOf("http") === 0) {
      return url;
    }
    var host = location.hostname;
    if (host.indexOf("github.io") !== -1 || host.indexOf("gitee.io") !== -1 || host.indexOf("gitcode.io") !== -1) {
      if (RELEASE_ONLY[item.id]) {
        return RELEASE_BASE + item.id + ".pdf";
      }
      if (host.indexOf("github.io") !== -1) {
        return JSDELIVR_BASE + url;
      }
    }
    return url;
  }

  function renderList() {
    referenceList.innerHTML = PDF_LIST.map(function (item) {
      return (
        '<div class="reference-item">' +
          '<span class="reference-text">' + escapeHtml(item.reference) + "</span>" +
          '<div class="pdf-card" data-id="' + item.id + '" role="button" tabindex="0">' +
            '<div class="pdf-mark"><span class="pdf-mark-text">PDF</span></div>' +
            '<div class="pdf-info">' +
              '<div class="pdf-title">' + escapeHtml(item.title) + "</div>" +
              '<div class="pdf-meta">' +
                '<span class="pdf-type">PDF ??</span>' +
                '<span class="pdf-size">' + escapeHtml(item.size) + "</span>" +
              "</div>" +
            "</div>" +
            '<span class="pdf-arrow">›</span>' +
          "</div>" +
        "</div>"
      );
    }).join("");

    referenceList.querySelectorAll(".pdf-card").forEach(function (card) {
      card.addEventListener("click", function () {
        var id = card.getAttribute("data-id");
        var paper = PDF_LIST.find(function (p) { return p.id === id; });
        if (paper) openPdf(paper);
      });
      card.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          card.click();
        }
      });
    });
  }

  function openPdf(paper) {
    activePdf = paper;
    readerTitle.textContent = paper.title;
    pdfFrame.src = resolvePdfUrl(paper) + "#toolbar=1&navpanes=0&view=FitH";
    homeView.classList.add("hidden");
    readerView.classList.remove("hidden");
    document.title = paper.title;
    if (history.pushState) {
      history.pushState({ id: paper.id }, "", "#/" + paper.id);
    }
  }

  function goHome() {
    activePdf = null;
    pdfFrame.src = "";
    readerView.classList.add("hidden");
    homeView.classList.remove("hidden");
    document.title = "????";
    if (history.pushState) {
      history.pushState({}, "", "#/");
    }
  }

  function openInNewTab() {
    if (activePdf) {
      window.open(resolvePdfUrl(activePdf), "_blank");
    }
  }

  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function restoreFromHash() {
    var hash = location.hash.replace(/^#\/?/, "");
    if (!hash) return;
    var paper = PDF_LIST.find(function (p) { return p.id === hash; });
    if (paper) openPdf(paper);
  }

  btnBack.addEventListener("click", goHome);
  btnOpenNew.addEventListener("click", openInNewTab);
  window.addEventListener("popstate", function () {
    var hash = location.hash.replace(/^#\/?/, "");
    if (!hash) {
      if (activePdf) {
        activePdf = null;
        pdfFrame.src = "";
        readerView.classList.add("hidden");
        homeView.classList.remove("hidden");
        document.title = "????";
      }
      return;
    }
    var paper = PDF_LIST.find(function (p) { return p.id === hash; });
    if (paper) openPdf(paper);
  });

  renderList();
  restoreFromHash();
})();
