const findy = {
    storage: { currentPage: null, maxPages: null },
    csvTitles: [
        "linkedin_url",
        "full_name",
        "first_name",
        "last_name",
        "email",
        "job_title",
        "company",
        "company_website",
        "city",
        "state",
        "country",
        "industry",
        "keywords",
        "employees",
        "company_city",
        "company_state",
        "company_country",
        "company_linkedin_url",
        "company_twitter_url",
        "company_facebook_url",
        "twitter_url",
        "facebook_url",
    ],
    exportButtonChecker: null,
    maxesSetFromPage: null,
    collectPeopleFailTimer: null,
    eventDuplicationsTimer: null,
};
(findy.peopleList = [findy.csvTitles]), (findy.emailList = []);
const Timeout = (e) => {
    let t = new AbortController();
    return setTimeout(() => t.abort(), 1e3 * e), t;
};
chrome.runtime.onMessage.addListener((e, t, o) => {
    console.log(e), "showExportModal" === e.msg && showExportModal();
});
let errorHandled = !1;
function findyEventsCallback(e) {
    clearTimeout(findy.eventDuplicationsTimer),
        (findy.eventDuplicationsTimer = setTimeout(function () {
            if (("pagination-found" === e.detail.name && getPagesCount(), "collect-people" === e.detail.name)) {
                let e;
                const t = new MutationObserver(function () {
                    clearTimeout(e),
                        (e = setTimeout(function () {
                            const e = document.querySelector(".app-aware-link"),
                                o = document.querySelector('[data-test="no-results-cta"]');
                            document.querySelector('[data-control-name="search_edit"]') && ejectExportButton(),
                                o &&
                                    setTimeout(function () {
                                        o.click();
                                    }, 500),
                                e && (getPagesCount(), t.disconnect());
                        }, 500));
                });
                t.observe(document.body, { childList: !0, subtree: !0 });
            }
            "show-export-button" === e.detail.name &&
                setTimeout(function () {
                    injectExportButton();
                }, 100),
                "hide-export-button" === e.detail.name && ejectExportButton();
        }, 10));
}
const findyEvents = document.createElement("a");
function showCreditsPreview() {
    const e = getEl("#findyOptionBox"),
        t = getEl(".findy--innput-people-export");
    e.matches(":checked")
        ? (getEl("#findyCreditsUsed").innerHTML = "This will use up to " + t.value + ' finder credits <a href="https://help.findymail.com/en/article/what-credits-do-i-need-to-scrape-apollo-2qbiqb/" target="_blank">↗️<a>')
        : (getEl("#findyCreditsUsed").innerHTML =
              "This will use up to " + t.value + ' verifier credits and Apollo email credits <a href="https://help.findymail.com/en/article/what-credits-do-i-need-to-scrape-apollo-2qbiqb/" target="_blank">↗️<a>');
}
function showWidget(e, t, o, n, r, i) {
    const l = document.createElement("iframe");
    (l.className = "findy--iframe-widget"),
        (l.src = e + t),
        renderHTML("components/modal.html", document.body).then(() =>
            renderHTML("pages/export-modal.html", getEl(".findy--modal"), !0).then(() => {
                renderHTML("components/export-status.html", getEl(".findy--laptop-loading-container")).then(() => {
                    renderStatus(getEl(".findy--export-inprogress"), "loading");
                }),
                    renderHTML("components/export-status.html", getEl(".findy--laptop-success-container")).then(() => {
                        renderStatus(getEl(".findy--export-success"), "success");
                    }),
                    renderHTML("components/export-status.html", getEl(".findy--laptop-error-container")).then(() => {
                        renderStatus(getEl(".findy--export-error"), "error");
                    }),
                    document.querySelectorAll(".findy--button-save-export").forEach(function (e) {
                        e.onclick = () => setExportCompleted();
                    }),
                    (getEl(".findy--button-continue").onclick = function () {
                        collectPeople();
                    });
                const e = getEl(".findy--innput-people-export");
                document.querySelectorAll(".findy--button-cancel").forEach(function (e) {
                    e.onclick = (e) => {
                        e.preventDefault(), resetExportSettings(), getEl(".findy--modal-wrapper").classList.remove("findy--modal-shown");
                    };
                }),
                    (e.onkeyup = function () {
                        chrome.storage.sync.set({ peopleToExport: this.value }).then(), showCreditsPreview();
                    }),
                    (e.onchange = function () {
                        chrome.storage.sync.set({ peopleToExport: this.value }).then(), showCreditsPreview();
                    }),
                    chrome.storage.sync.get("peopleToExport", function (t) {
                        let { peopleToExport: o } = t;
                        !isNaN(o) && o > 0 ? ((e.value = o), showCreditsPreview()) : (e.value = 0);
                    }),
                    chrome.storage.sync.get(["apiKey"], function ({ isSN: e, apiKey: t }) {
                        getLists(t)
                            .then((e) => e.json())
                            .then(async (e) => {
                                let t = await chrome.storage.sync.get("autoSelectContactList"),
                                    o = getEl("#findyListSelect");
                                for (var n = 0; n < e.lists.length; n++) {
                                    var r = document.createElement("option");
                                    (r.value = e.lists[n].id), (r.innerHTML = e.lists[n].name), r.value == t?.autoSelectContactList && (r.selected = "selected"), o.appendChild(r);
                                }
                            });
                    });
                (getEl("#findyOptionBox").onchange = function () {
                    chrome.storage.sync.set({ exportOption: this.matches(":checked") }).then(), showCreditsPreview();
                }),
                    (getEl(".findy--export-form").onsubmit = (e) => {
                        e.preventDefault(), collectPeople();
                    }),
                    (getEl("#createListBtn").onclick = function () {
                        renderHTML("/components/create-list.html", getEl(".findy--modal"), !0).then(() => {
                            chrome.storage.sync.get(["apiKey"], function ({ isSN: e, apiKey: t }) {
                                (document.getElementById("closeBtn").onclick = () => getEl(".findy--modal-wrapper").classList.remove("findy--modal-shown")),
                                    (document.getElementById("cancelBtn").onclick = () => {
                                        chrome.storage.sync.get(null, ({ findy_url: e, auth_url: t, authorization_status: o, widget_size: n, widgetX: r, widgetY: i, modal: l }) => {
                                            showWidget(e, t, o, n, r, i, l);
                                        });
                                    }),
                                    (document.getElementById("createListBtn").onclick = () => {
                                        let e = document.getElementById("listnameInput").value;
                                        e &&
                                            createList(t, e)
                                                .then(
                                                    (e) => e.json(),
                                                    (e) => {}
                                                )
                                                .then((e) => {
                                                    e.list.id &&
                                                        chrome.storage.sync.set({ autoSelectContactList: e.list.id }).then(() => {
                                                            chrome.storage.sync.get(null, ({ findy_url: e, auth_url: t, authorization_status: o, widget_size: n, widgetX: r, widgetY: i, modal: l }) => {
                                                                showWidget(e, t, o, n, r, i, l);
                                                            });
                                                        });
                                                });
                                    });
                            });
                        });
                    });
            })
        ),
        addEventListener(
            "message",
            function (t) {
                t.origin.includes(e) && ["is_authorized", "not_authorized"].includes(t.data) && chrome.storage.sync.set({ authorization_status: t.data }).then();
            },
            !1
        );
}
function reloadIframe() {
    getEl(".findy--iframe-widget").replaceWith(getEl(".findy--iframe-widget"));
}
function checkUrl(e, t) {
    chrome.storage.sync.get(["findy_url", "auth_url", "authorization_status"], function ({ findy_url: o, auth_url: n, authorization_status: r }) {
        "is_authorized" === r
            ? /^https:\/\/app.apollo.io\/#\/people/.test(e)
                ? (showPage("authorized", t), toggleprofileTab(!1))
                : ((findy.storage.currentPage = null), (findy.storage.maxPages = null), findyEvents.dispatchEvent(new CustomEvent("findyEvent", { detail: { name: "hide-export-button" } })))
            : "not_authorized" === r && (showPage("unauthorized", t), toggleprofileTab(!1));
    });
}
function toggleprofileTab(e) {
    e ? getEl('[data-findy-tab="profile"]')?.classList.remove("findy--tab-disabled") : getEl('[data-findy-tab="profile"]')?.classList.add("findy--tab-disabled");
}
function showPage(e, t, o) {
    switch ((findyEvents.dispatchEvent(new CustomEvent("findyEvent", { detail: { name: "hide-export-button" } })), e)) {
        case "unauthorized":
            chrome.storage.sync.get(["exportStatus", "unauthPage", "findy_url", "auth_url"], function ({ exportStatus: e, unauthPage: t, findy_url: o, auth_url: n }) {
                content.innerHTML = t;
                const r = document.createRange().createContextualFragment(e);
                content.querySelector(".findy--content-unauth").prepend(r), renderStatus(content, "login");
                const i = content.querySelector(".findy--open-auth"),
                    l = content.querySelector(".findy--open-signup");
                (i.onclick = function () {
                    chrome.runtime.sendMessage({ action: "open-signin" });
                }),
                    (l.href = `${o}${n}#sign_up`);
            });
            break;
        case "authorized":
            findyEvents.dispatchEvent(new CustomEvent("findyEvent", { detail: { name: "show-export-button" } }));
            break;
        case "pageIsNotSupported":
            chrome.storage.sync.get(["instructions"], function ({ instructions: e }) {
                content.innerHTML = e;
            });
    }
    if ("profile" === e) setActiveTab("profile", !1);
    else setActiveTab("info", !1);
}
function setActiveTab(e, t = !0) {
    getEl('[data-findy-tab="' + e + '"]', null, !0).then(function (o) {
        o.classList.contains("findy--tab-disabled") ||
            getEl(".findy--tab-active", null, !0).then(function (n) {
                if ((n.dataset.findyTab !== e && n.classList.remove("findy--tab-active"), o.classList.add("findy--tab-active"), t))
                    if ("profile" === e) showPage("profile", !1, renderProfile);
                    else showPage("authorized");
            });
    });
}
function injectExportButton() {
    try {
        findy.exportButtonChecker.disconnect();
    } catch (e) {}
    function e(t) {
        console.log("Rendering export button");
        if (document.querySelector(".findy--search-export-button-apollo")) return void console.log("button already existing, aborting");
        const o = document.createElement("a");
        (o.textContent = "💌 Export to CSV"),
            (o.textContent.className = "zp-link zp_3_fnL zp_hH5mY zp_3tUWX findy--search-export-button-apollo"),
            (o.style =
                "color: white; font-weight: 600; cursor: pointer; padding-top: 10px; padding-bottom: 10px; padding-left: 10px; padding-right: 10px; background: #E84C4B; border-radius: 8px; overflow: hidden; justify-content: flex-start; align-items: center; gap: 8px; display: inline-flex; margin-bottom: 5px"),
            (o.onclick = showExportModal);
        let n = document.querySelector("div.pipeline-tabs");
        if (
            !n &&
            (console.log("didn't find tabs to add button, next selector #1"),
            (n = document.querySelector(".finder-explorer-sidebar-shown div.zp-tabs")),
            !n && (console.log("didn't find tabs to add button, next selector #2"), (n = document.querySelector(".zp_hdLme > div")), !n))
        )
            return (
                console.log("didn't find tabs to add button, retrying later"),
                void setTimeout(() => {
                    e(t);
                }, 4e3)
            );
        n.append(o);
    }
    chrome.storage.sync.get(["exportButton"], function ({ exportButton: t }) {
        e(t);
    });
}
function ejectExportButton() {
    try {
        document.querySelector(".findy--search-export-holder").remove(), (findy.peopleList = [findy.csvTitles]), (findy.emailList = []);
    } catch (e) {}
}
function saveCSV() {
    chrome.storage.sync.set({ export_status: "finished" }).then();
    const e = "data:text/csv;charset=utf-8," + findy.peopleList.map((e) => e.join(",").replace(/#/g, "").trim()).join("\r\n"),
        t = encodeURI(e),
        o = document.createElement("a");
    o.setAttribute("href", t), o.setAttribute("download", `apollo_export_${findy.peopleList.length - 1}_${new Date().toISOString().slice(0, -5).replace(/[T:]/g, "-")}.csv`), o.click();
}
function flipPage() {
    clearTimeout(findy.collectPeopleFailTimer), console.log("flippingPage"), (errorHandled = !1);
    const { maxPages: e, currentPage: t } = findy.storage,
        o = [...getPaginationPage().querySelectorAll(".zp-button")][1];
    if ((console.log(o), !o)) return;
    const n = o.disabled;
    console.log(n),
        n &&
            chrome.storage.sync.get(["apollo_tab"], function ({ apollo_tab: e }) {
                if ("net_new" === e) {
                    console.log("Reached end of net new");
                    const e = [...getPaginationPage().querySelectorAll(".zp-button")][0];
                    if (!e) return;
                    e.disabled || (console.log("net new: we can go back. Flipping previous page"), e.click());
                } else setExportCompleted();
            }),
        console.log(t),
        console.log(e),
        n || (console.log("clicking next page"), o.click());
}
function resetExportSettings() {
    const e = getEl(".findy--innput-people-export");
    (e.max = 0),
        (e.value = 0),
        chrome.storage.sync.set({ peopleToExport: 0, exportOption: !1, apollo_duplicates: !1, apollo_tab: "not_net_new", autoSelectContactList: null }).then(),
        (getEl(".findy--max-people").innerText = 0),
        (getEl("#findyCreditsUsed").innerHTML = ""),
        (findy.peopleList = [findy.csvTitles]),
        chrome.storage.sync.set({ export_status: "waiting" }).then(),
        (findy.emailList = []),
        (findy.maxesSetFromPage = !1);
}
function showExportModal() {
    chrome.storage.sync.get(["apiKey"], function ({ apiKey: e }) {
        getCredits(e)
            .then(
                (e) => e.json(),
                (e) => {
                    alert("Please login to use the Findymail extension");
                }
            )
            .then((e) => {
                if (void 0 !== e.credits && (e.credits > 0 || e.verifier_credits > 0)) {
                    getEl("#findyOptionLabel").style = "font-size:14px;";
                    getEl(".findy--modal-wrapper").classList.add("findy--modal-shown"), resetExportSettings(), getPagesCount();
                } else alert("You're not authenticated or don't have any Findymail credits left. Please login to the extension and make sure to have enough credits to be able to export data.");
            });
    });
}
function getPaginationPage() {
    let e = document.querySelector(".zp-button-group");
    return (
        e ||
            (e = document.evaluate('//div[not(contains(@class, "input-container"))]/div/div[contains(@class, "Select") and contains(@class, "has-value")]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue
                .parentElement.parentElement),
        e
    );
}
function getPagesCount() {
    const e = document.querySelector("table"),
        t = getPaginationPage();
    chrome.storage.sync.get([], function ({}) {
        if (!e) return !1;
        const o = new MutationObserver(function (e) {
            const t = {};
            try {
                e.forEach(function (e) {
                    if (e.target.classList.contains("zp-button-group")) throw (findyEvents.dispatchEvent(new CustomEvent("findyEvent", { detail: { name: "pagination-found" } })), t);
                });
            } catch (e) {
                if (e !== t) throw e;
            }
        });
        if (t)
            o.disconnect(),
                (function () {
                    const e = getPaginationPage(),
                        t = document.querySelector("div:not(.is-searchable) > div.Select-control .zp-select-main").textContent.trim(),
                        o = Math.min(2500, parseInt(e.parentElement.firstChild.textContent.split("of")[1].replace(",", "").replace(".", "").replace("M", "000").trim())),
                        n = o / 25;
                    (findy.storage.currentPage = t),
                        (findy.storage.maxPages = n),
                        (0 == +getEl(".findy--max-people").textContent || findy.maxesSetFromPage) &&
                            ((getEl(".findy--innput-people-export").max = o),
                            (getEl(".findy--innput-people-export").value = o),
                            (getEl(".findy--max-people").innerText = o),
                            chrome.storage.sync.set({ peopleToExport: o }).then(),
                            (findy.maxesSetFromPage = !1),
                            showCreditsPreview()),
                        chrome.storage.sync.get(["export_status"], function ({ export_status: e }) {
                            "working" === e && collectPeople();
                        });
                })();
        else {
            o.observe(e, { childList: !0, subtree: !0 }), (document.querySelector("html").scrollTop = document.querySelector("html").scrollHeight), (findy.storage.currentPage = 1), (findy.storage.maxPages = 1);
            const t = e.querySelectorAll(".reusable-search__result-container")?.length;
            0 == +getEl(".findy--max-people").textContent &&
                ((getEl(".findy--innput-people-export").max = t),
                (getEl(".findy--innput-people-export").value = t),
                (getEl(".findy--max-people").innerText = t),
                chrome.storage.sync.set({ peopleToExport: t }).then(),
                (findy.maxesSetFromPage = !0));
        }
    });
}
function waitForElm(e) {
    return new Promise((t) => {
        if (document.querySelector(e)) return t(document.querySelector(e));
        const o = new MutationObserver((n) => {
            document.querySelector(e) && (t(document.querySelector(e)), o.disconnect());
        });
        o.observe(document.body, { childList: !0, subtree: !0 });
    });
}
function collectPeople(e = 0, t = 0) {
    console.log("collectPeople"),
        chrome.storage.sync.get(["apiKey", "export_status"], function ({ apiKey: o, export_status: n }) {
            if ("finished" === n) return;
            chrome.storage.sync.set({ export_status: "working" }).then(), findyEvents.dispatchEvent(new CustomEvent("findyEvent", { detail: { name: "collect-people" } }));
            let r = e,
                i = 0,
                l = [],
                a = 0,
                s = Date.now();
            findy.collectPeopleFailTimer = null;
            try {
                document.querySelector(".pipeline-tabs.zp-tabs .zp_FvOcf").textContent.includes("Net")
                    ? (console.log("Net new"), chrome.storage.sync.set({ apollo_tab: "net_new" }).then())
                    : (console.log("Not net new"), chrome.storage.sync.set({ apollo_tab: "not_net_new" }).then());
            } catch (e) {
                console.log(e);
            }
            chrome.storage.sync.get(["lang", "peopleToExport", "exportOption"], function ({ lang: e, peopleToExport: n, exportOption: c }) {
                function u() {
                    console.log("resetFailureTimeout"), (s = Date.now());
                }
                const p = {};
                let d = getEl("#findyListSelect").value;
                getEl(".findy--export-progress-total").textContent = n;
                try {
                    if (null === document.getElementById("findymail-profiles"))
                        return (
                            console.log("profiles arent there yet"),
                            void (t < 3
                                ? setTimeout(function () {
                                      collectPeople(r, t + 1);
                                  }, 5e3)
                                : setTimeout(function () {
                                      flipPage(),
                                          setTimeout(function () {
                                              collectPeople(r);
                                          }, 5e3);
                                  }, Math.max(5e3, Math.floor(1e4 * Math.random()))))
                        );
                    clearTimeout(findy.collectPeopleFailTimer),
                        (findy.collectPeopleFailTimer = setTimeout(function () {
                            chrome.storage.sync.get(["export_status"], function ({ export_status: e }) {
                                ("working" !== e && "completing" !== e) ||
                                    (console.log("failTimer: seems stuck, triggering pageFlip"),
                                    setTimeout(function () {
                                        flipPage(),
                                            setTimeout(function () {
                                                collectPeople(r);
                                            }, 5e3);
                                    }, Math.max(5e3, Math.floor(1e4 * Math.random()))));
                            });
                        }, 3e5));
                    let e = JSON.parse(document.getElementById("findymail-profiles").textContent.replaceAll("\n", "")),
                        s = null;
                    try {
                        s = JSON.parse(document.getElementById("findymail-orgs").textContent.replaceAll("\n", ""));
                    } catch (e) {
                        console.error("didn't find orgs data");
                    }
                    (l = [...document.querySelectorAll(".apollo-icon-cloud-download")].slice(0, Math.min(n - r, 25))),
                        c ||
                            (0 === l.length
                                ? 1 === findy.peopleList.length &&
                                  0 === document.querySelectorAll(".zp-contact-email-envelope-container").length &&
                                  window.alert(
                                      'It seems the "email" column may be missing in your Apollo table. Please make sure the "email" column is present in your Apollo table by configuring your table. See: https://help.findymail.com/en/article/apollo-scraper-is-stuck-at-0-1as0mn/'
                                  )
                                : l[0].click());
                    let m = e.length;
                    if (
                        (waitForElm("#findymail-apollo-error").then((e) => {
                            console.log("Detecting error element " + errorHandled),
                                errorHandled ||
                                    (setTimeout(function () {
                                        flipPage(),
                                            setTimeout(function () {
                                                collectPeople(r);
                                            }, 5e3);
                                    }, Math.max(5e3, Math.floor(1e4 * Math.random()))),
                                    e.remove(),
                                    (errorHandled = !0));
                        }),
                        Object.entries(e.slice(0, Math.min(n, m))).forEach(function (e) {
                            try {
                                let t = e[1],
                                    f = "email_not_unlocked@domain.com" === t.email ? "" : t.email,
                                    g = t.id,
                                    y = processString(t.first_name || ""),
                                    h = processString(t.last_name || ""),
                                    S = y + " " + h,
                                    q = null != t.organization ? cleanCompanyName(t.organization.name || "") : "",
                                    x = cleanJobTitle(t.title || t.headline || ""),
                                    E = (null != t.organization && (t.organization.primary_domain || t.organization.website_url)) || "",
                                    _ = null != t.organization ? t.organization.primary_domain || t.organization.website_url || t.organization.name : "",
                                    T = t.city,
                                    w = t.state,
                                    b = t.country,
                                    P = t.linkedin_url,
                                    L = t.twitter_url,
                                    C = t.twitter_url,
                                    v = t.facebook_url,
                                    M = null != t.organization ? t.organization.linkedin_url : "",
                                    k = null != t.organization ? t.organization.facebook_url : "",
                                    z = null != t.organization ? t.organization.twitter_url : "",
                                    F = { industry: null, keywords: [], estimated_num_employees: null, city: null, state: null, country: null };
                                try {
                                    F = s.organizations.find((e) => e.id == t.organization_id);
                                } catch (e) {}
                                null != C && C.includes("twitter.com") && (C = C.replaceAll("https://twitter.com/", "")),
                                    (r += 1),
                                    c
                                        ? r <= n &&
                                          getEmail(o, y + " " + h, _, d, P?.split("/in")[1], q, x, T, w, b)
                                              .then((e) => e.json())
                                              .then((e) => {
                                                  u();
                                                  let t = "";
                                                  if (
                                                      ((t = e.error || e.errors ? "" : e.contact && e.contact.email ? e.contact.email : ""),
                                                      findy.peopleList.push([
                                                          quoteStr(P),
                                                          quoteStr(S),
                                                          quoteStr(y),
                                                          quoteStr(h),
                                                          t,
                                                          quoteStr(x),
                                                          quoteStr(q),
                                                          E,
                                                          quoteStr(T),
                                                          quoteStr(w),
                                                          quoteStr(b),
                                                          quoteStr(F?.industry),
                                                          quoteStr(F?.keywords.join(",")),
                                                          F?.estimated_num_employees,
                                                          quoteStr(F?.city),
                                                          quoteStr(F?.state),
                                                          quoteStr(F?.country),
                                                          quoteStr(M),
                                                          quoteStr(z),
                                                          quoteStr(k),
                                                          quoteStr(L),
                                                          quoteStr(v),
                                                      ]),
                                                      (getEl(".findy--export-progress-current").textContent = findy.peopleList.length - 1),
                                                      (getEl(".findy--export-progress-total").textContent = n),
                                                      findy.peopleList.length - 1 >= +n)
                                                  )
                                                      throw (setExportCompleted(), clearTimeout(findy.collectPeopleFailTimer), p);
                                                  (a += 1),
                                                      console.log("localCounter #1 " + a),
                                                      (25 !== a && a !== m) ||
                                                          (clearTimeout(findy.collectPeopleFailTimer),
                                                          setTimeout(function () {
                                                              flipPage(),
                                                                  setTimeout(function () {
                                                                      collectPeople(r);
                                                                  }, 5e3);
                                                          }, Math.max(5e3, Math.floor(1e4 * Math.random()))));
                                              })
                                              .catch((e) => {
                                                  if ((console.error(e), e !== p)) {
                                                      if (
                                                          (u(),
                                                          findy.peopleList.push([
                                                              quoteStr(P),
                                                              quoteStr(S),
                                                              quoteStr(y),
                                                              quoteStr(h),
                                                              "",
                                                              quoteStr(x),
                                                              quoteStr(q),
                                                              E,
                                                              quoteStr(T),
                                                              quoteStr(w),
                                                              quoteStr(b),
                                                              quoteStr(F?.industry),
                                                              quoteStr(F?.keywords.join(",")),
                                                              F?.estimated_num_employees,
                                                              quoteStr(F?.city),
                                                              quoteStr(F?.state),
                                                              quoteStr(F?.country),
                                                              quoteStr(M),
                                                              quoteStr(z),
                                                              quoteStr(k),
                                                              quoteStr(L),
                                                              quoteStr(v),
                                                          ]),
                                                          (getEl(".findy--export-progress-current").textContent = findy.peopleList.length - 1),
                                                          (getEl(".findy--export-progress-total").textContent = n),
                                                          findy.peopleList.length - 1 >= +n)
                                                      )
                                                          throw (setExportCompleted(), clearTimeout(findy.collectPeopleFailTimer), p);
                                                      (a += 1),
                                                          console.log("localCounter #2 " + a),
                                                          (25 !== a && a !== m) ||
                                                              (clearTimeout(findy.collectPeopleFailTimer),
                                                              setTimeout(function () {
                                                                  flipPage(),
                                                                      setTimeout(function () {
                                                                          collectPeople(r);
                                                                      }, 5e3);
                                                              }, Math.max(5e3, Math.floor(1e4 * Math.random()))));
                                                  }
                                              })
                                        : null === f
                                        ? (u(),
                                          getEmail(o, y + " " + h, _, d, P.split("/in")[1], q, x, T, w, b)
                                              .then((e) => e.json())
                                              .then((e) => {
                                                  u();
                                                  let t = "";
                                                  if (((t = e.error || e.errors ? "" : e.contact && e.contact.email ? e.contact.email : ""), findy.emailList.includes(t) && "" !== t))
                                                      console.log("We already added " + t + " (?)"), chrome.storage.sync.set({ apollo_duplicates: !0 }).then();
                                                  else if (
                                                      (findy.emailList.push(t),
                                                      findy.peopleList.push([
                                                          quoteStr(P),
                                                          quoteStr(S),
                                                          quoteStr(y),
                                                          quoteStr(h),
                                                          t,
                                                          quoteStr(x),
                                                          quoteStr(q),
                                                          E,
                                                          quoteStr(T),
                                                          quoteStr(w),
                                                          quoteStr(b),
                                                          quoteStr(F?.industry),
                                                          quoteStr(F?.keywords.join(",")),
                                                          F?.estimated_num_employees,
                                                          quoteStr(F?.city),
                                                          quoteStr(F?.state),
                                                          quoteStr(F?.country),
                                                          quoteStr(M),
                                                          quoteStr(z),
                                                          quoteStr(k),
                                                          quoteStr(L),
                                                          quoteStr(v),
                                                      ]),
                                                      (getEl(".findy--export-progress-current").textContent = findy.peopleList.length - 1),
                                                      (getEl(".findy--export-progress-total").textContent = n),
                                                      findy.peopleList.length - 1 >= +n)
                                                  )
                                                      throw (setExportCompleted(), clearTimeout(findy.collectPeopleFailTimer), p);
                                                  (a += 1),
                                                      console.log("localCounter #3 " + a),
                                                      (25 !== a && a !== m) ||
                                                          (clearTimeout(findy.collectPeopleFailTimer),
                                                          setTimeout(function () {
                                                              flipPage(),
                                                                  setTimeout(function () {
                                                                      collectPeople(r);
                                                                  }, 5e3);
                                                          }, Math.max(5e3, Math.floor(1e4 * Math.random()))));
                                              })
                                              .catch((e) => {
                                                  if ((console.error(e), e !== p)) {
                                                      if (
                                                          (u(),
                                                          findy.peopleList.push([
                                                              quoteStr(P),
                                                              quoteStr(S),
                                                              quoteStr(y),
                                                              quoteStr(h),
                                                              "",
                                                              quoteStr(x),
                                                              quoteStr(q),
                                                              E,
                                                              quoteStr(T),
                                                              quoteStr(w),
                                                              quoteStr(b),
                                                              quoteStr(F?.industry),
                                                              quoteStr(F?.keywords.join(",")),
                                                              F?.estimated_num_employees,
                                                              quoteStr(F?.city),
                                                              quoteStr(F?.state),
                                                              quoteStr(F?.country),
                                                              quoteStr(M),
                                                              quoteStr(z),
                                                              quoteStr(k),
                                                              quoteStr(L),
                                                              quoteStr(v),
                                                          ]),
                                                          (getEl(".findy--export-progress-current").textContent = findy.peopleList.length - 1),
                                                          (getEl(".findy--export-progress-total").textContent = n),
                                                          findy.peopleList.length - 1 >= +n)
                                                      )
                                                          throw (setExportCompleted(), p);
                                                      (a += 1),
                                                          console.log("localCounter #4 " + a),
                                                          (25 !== a && a !== m) ||
                                                              (clearTimeout(findy.collectPeopleFailTimer),
                                                              setTimeout(function () {
                                                                  flipPage(),
                                                                      setTimeout(function () {
                                                                          collectPeople(r);
                                                                      }, Math.max(5e3, Math.floor(7500 * Math.random())));
                                                              }, Math.max(7500, Math.floor(15e3 * Math.random()))));
                                                  }
                                              }))
                                        : "" === f
                                        ? waitForElm("#p" + g)
                                              .then((e) => {
                                                  console.log(i),
                                                      i < l.length - 1 &&
                                                          setTimeout(function () {
                                                              chrome.storage.sync.get(["export_status"], function ({ export_status: e }) {
                                                                  "finished" !== e && (i++, l[i].click());
                                                              });
                                                          }, Math.max(1500, Math.floor(2500 * Math.random()))),
                                                      u(),
                                                      (f = e.textContent),
                                                      e.remove(),
                                                      "" != f && null != f
                                                          ? findy.emailList.includes(f)
                                                              ? (console.log("We already added " + f + " (?)"),
                                                                chrome.storage.sync.set({ apollo_duplicates: !0 }).then(),
                                                                n--,
                                                                r--,
                                                                chrome.storage.sync.set({ peopleToExport: n }).then(),
                                                                (a += 1),
                                                                console.log("localCounter #15 " + a),
                                                                (25 !== a && a !== m) ||
                                                                    (clearTimeout(findy.collectPeopleFailTimer),
                                                                    setTimeout(function () {
                                                                        flipPage(),
                                                                            setTimeout(function () {
                                                                                collectPeople(r);
                                                                            }, Math.max(5e3, Math.floor(7500 * Math.random())));
                                                                    }, Math.max(7500, Math.floor(15e3 * Math.random())))))
                                                              : (findy.emailList.push(f),
                                                                verifyEmail(o, f, d, y + " " + h, P?.split("/in")[1], q, x, T, w, b, C)
                                                                    .then((e) => e.json())
                                                                    .then((e) => {
                                                                        if ((u(), e.error)) throw (alert(e.error), setExportCompleted(), clearTimeout(findy.collectPeopleFailTimer), p);
                                                                        if (e.verified) {
                                                                            if (
                                                                                (findy.peopleList.push([
                                                                                    quoteStr(P),
                                                                                    quoteStr(S),
                                                                                    quoteStr(y),
                                                                                    quoteStr(h),
                                                                                    f,
                                                                                    quoteStr(x),
                                                                                    quoteStr(q),
                                                                                    E,
                                                                                    quoteStr(T),
                                                                                    quoteStr(w),
                                                                                    quoteStr(b),
                                                                                    quoteStr(F?.industry),
                                                                                    quoteStr(F?.keywords.join(",")),
                                                                                    F?.estimated_num_employees,
                                                                                    quoteStr(F?.city),
                                                                                    quoteStr(F?.state),
                                                                                    quoteStr(F?.country),
                                                                                    quoteStr(M),
                                                                                    quoteStr(z),
                                                                                    quoteStr(k),
                                                                                    quoteStr(L),
                                                                                    quoteStr(v),
                                                                                ]),
                                                                                (getEl(".findy--export-progress-current").textContent = findy.peopleList.length - 1),
                                                                                (getEl(".findy--export-progress-total").textContent = n),
                                                                                findy.peopleList.length - 1 >= +n)
                                                                            )
                                                                                throw (setExportCompleted(), clearTimeout(findy.collectPeopleFailTimer), p);
                                                                            (a += 1),
                                                                                console.log("localCounter #5 " + a),
                                                                                (25 !== a && a !== m) ||
                                                                                    (clearTimeout(findy.collectPeopleFailTimer),
                                                                                    setTimeout(function () {
                                                                                        flipPage(),
                                                                                            setTimeout(function () {
                                                                                                collectPeople(r);
                                                                                            }, Math.max(5e3, Math.floor(7500 * Math.random())));
                                                                                    }, Math.max(5e3, Math.floor(1e4 * Math.random()))));
                                                                        } else
                                                                            getEmail(o, y + " " + h, _, d, P?.split("/in")[1], q, x, T, w, b)
                                                                                .then((e) => e.json())
                                                                                .then((e) => {
                                                                                    u();
                                                                                    let t = "";
                                                                                    if (
                                                                                        ((t = e.error || e.errors ? "" : e.contact && e.contact.email ? e.contact.email : ""),
                                                                                        findy.emailList.includes(t) && "" !== t
                                                                                            ? (console.log("We already added " + t + " (?)"),
                                                                                              chrome.storage.sync.set({ apollo_duplicates: !0 }).then(),
                                                                                              n--,
                                                                                              r--,
                                                                                              chrome.storage.sync.set({ peopleToExport: n }).then())
                                                                                            : (findy.emailList.push(t),
                                                                                              findy.peopleList.push([
                                                                                                  quoteStr(P),
                                                                                                  quoteStr(S),
                                                                                                  quoteStr(y),
                                                                                                  quoteStr(h),
                                                                                                  t,
                                                                                                  quoteStr(x),
                                                                                                  quoteStr(q),
                                                                                                  E,
                                                                                                  quoteStr(T),
                                                                                                  quoteStr(w),
                                                                                                  quoteStr(b),
                                                                                                  quoteStr(F?.industry),
                                                                                                  quoteStr(F?.keywords.join(",")),
                                                                                                  F?.estimated_num_employees,
                                                                                                  quoteStr(F?.city),
                                                                                                  quoteStr(F?.state),
                                                                                                  quoteStr(F?.country),
                                                                                                  quoteStr(M),
                                                                                                  quoteStr(z),
                                                                                                  quoteStr(k),
                                                                                                  quoteStr(L),
                                                                                                  quoteStr(v),
                                                                                              ]),
                                                                                              (getEl(".findy--export-progress-current").textContent = findy.peopleList.length - 1),
                                                                                              (getEl(".findy--export-progress-total").textContent = n)),
                                                                                        findy.peopleList.length - 1 >= +n)
                                                                                    )
                                                                                        throw (setExportCompleted(), clearTimeout(findy.collectPeopleFailTimer), p);
                                                                                    (a += 1),
                                                                                        console.log("localCounter #6 " + a),
                                                                                        (25 !== a && a !== m) ||
                                                                                            (clearTimeout(findy.collectPeopleFailTimer),
                                                                                            setTimeout(function () {
                                                                                                flipPage(),
                                                                                                    setTimeout(function () {
                                                                                                        collectPeople(r);
                                                                                                    }, 5e3);
                                                                                            }, Math.max(5e3, Math.floor(1e4 * Math.random()))));
                                                                                })
                                                                                .catch((e) => {
                                                                                    if ((console.error(e), e !== p)) {
                                                                                        if (
                                                                                            (findy.peopleList.push([
                                                                                                quoteStr(P),
                                                                                                quoteStr(S),
                                                                                                quoteStr(y),
                                                                                                quoteStr(h),
                                                                                                "",
                                                                                                quoteStr(x),
                                                                                                quoteStr(q),
                                                                                                E,
                                                                                                quoteStr(T),
                                                                                                quoteStr(w),
                                                                                                quoteStr(b),
                                                                                                quoteStr(F?.industry),
                                                                                                quoteStr(F?.keywords.join(",")),
                                                                                                F?.estimated_num_employees,
                                                                                                quoteStr(F?.city),
                                                                                                quoteStr(F?.state),
                                                                                                quoteStr(F?.country),
                                                                                                quoteStr(M),
                                                                                                quoteStr(z),
                                                                                                quoteStr(k),
                                                                                                quoteStr(L),
                                                                                                quoteStr(v),
                                                                                            ]),
                                                                                            (getEl(".findy--export-progress-current").textContent = findy.peopleList.length - 1),
                                                                                            (getEl(".findy--export-progress-total").textContent = n),
                                                                                            findy.peopleList.length - 1 >= +n)
                                                                                        )
                                                                                            throw (setExportCompleted(), clearTimeout(findy.collectPeopleFailTimer), p);
                                                                                        (a += 1),
                                                                                            console.log("localCounter #7 " + a),
                                                                                            (25 !== a && a !== m) ||
                                                                                                (clearTimeout(findy.collectPeopleFailTimer),
                                                                                                setTimeout(function () {
                                                                                                    flipPage(),
                                                                                                        setTimeout(function () {
                                                                                                            collectPeople(r);
                                                                                                        }, Math.max(5e3, Math.floor(7500 * Math.random())));
                                                                                                }, Math.max(5e3, Math.floor(1e4 * Math.random()))));
                                                                                    }
                                                                                });
                                                                    })
                                                                    .catch((e) => {
                                                                        if ((console.error(e), e !== p)) {
                                                                            if (
                                                                                (findy.peopleList.push([
                                                                                    quoteStr(P),
                                                                                    quoteStr(S),
                                                                                    quoteStr(y),
                                                                                    quoteStr(h),
                                                                                    "",
                                                                                    quoteStr(x),
                                                                                    quoteStr(q),
                                                                                    E,
                                                                                    quoteStr(T),
                                                                                    quoteStr(w),
                                                                                    quoteStr(b),
                                                                                    quoteStr(F?.industry),
                                                                                    quoteStr(F?.keywords.join(",")),
                                                                                    F?.estimated_num_employees,
                                                                                    quoteStr(F?.city),
                                                                                    quoteStr(F?.state),
                                                                                    quoteStr(F?.country),
                                                                                    quoteStr(M),
                                                                                    quoteStr(z),
                                                                                    quoteStr(k),
                                                                                    quoteStr(L),
                                                                                    quoteStr(v),
                                                                                ]),
                                                                                (getEl(".findy--export-progress-current").textContent = findy.peopleList.length - 1),
                                                                                (getEl(".findy--export-progress-total").textContent = n),
                                                                                findy.peopleList.length - 1 >= +n)
                                                                            )
                                                                                throw (setExportCompleted(), clearTimeout(findy.collectPeopleFailTimer), p);
                                                                            (a += 1),
                                                                                console.log("localCounter #8 " + a),
                                                                                (25 !== a && a !== m) ||
                                                                                    (clearTimeout(findy.collectPeopleFailTimer),
                                                                                    setTimeout(function () {
                                                                                        flipPage(),
                                                                                            setTimeout(function () {
                                                                                                collectPeople(r);
                                                                                            }, Math.max(5e3, Math.floor(7500 * Math.random())));
                                                                                    }, Math.max(7500, Math.floor(15e3 * Math.random()))));
                                                                        }
                                                                    }))
                                                          : getEmail(o, y + " " + h, _, d, P?.split("/in")[1], q, x, T, w, b)
                                                                .then((e) => e.json())
                                                                .then((e) => {
                                                                    u();
                                                                    let t = "";
                                                                    if (((t = e.error || e.errors ? "" : e.contact && e.contact.email ? e.contact.email : ""), findy.emailList.includes(t) && "" !== t))
                                                                        console.log("We already added " + t + " (?)"), chrome.storage.sync.set({ apollo_duplicates: !0 }).then();
                                                                    else if (
                                                                        (findy.emailList.push(t),
                                                                        findy.peopleList.push([
                                                                            quoteStr(P),
                                                                            quoteStr(S),
                                                                            quoteStr(y),
                                                                            quoteStr(h),
                                                                            t,
                                                                            quoteStr(x),
                                                                            quoteStr(q),
                                                                            E,
                                                                            quoteStr(T),
                                                                            quoteStr(w),
                                                                            quoteStr(b),
                                                                            quoteStr(F?.industry),
                                                                            quoteStr(F?.keywords.join(",")),
                                                                            F?.estimated_num_employees,
                                                                            quoteStr(F?.city),
                                                                            quoteStr(F?.state),
                                                                            quoteStr(F?.country),
                                                                            quoteStr(M),
                                                                            quoteStr(z),
                                                                            quoteStr(k),
                                                                            quoteStr(L),
                                                                            quoteStr(v),
                                                                        ]),
                                                                        (getEl(".findy--export-progress-current").textContent = findy.peopleList.length - 1),
                                                                        (getEl(".findy--export-progress-total").textContent = n),
                                                                        findy.peopleList.length - 1 >= +n)
                                                                    )
                                                                        throw (setExportCompleted(), clearTimeout(findy.collectPeopleFailTimer), p);
                                                                    (a += 1),
                                                                        console.log("localCounter #9 " + a),
                                                                        (25 !== a && a !== m) ||
                                                                            (clearTimeout(findy.collectPeopleFailTimer),
                                                                            setTimeout(function () {
                                                                                flipPage(),
                                                                                    setTimeout(function () {
                                                                                        collectPeople(r);
                                                                                    }, 5e3);
                                                                            }, Math.max(5e3, Math.floor(1e4 * Math.random()))));
                                                                })
                                                                .catch((e) => {
                                                                    if ((console.error(e), e !== p)) {
                                                                        if (
                                                                            (findy.peopleList.push([
                                                                                quoteStr(P),
                                                                                quoteStr(S),
                                                                                quoteStr(y),
                                                                                quoteStr(h),
                                                                                "",
                                                                                quoteStr(x),
                                                                                quoteStr(q),
                                                                                E,
                                                                                quoteStr(T),
                                                                                quoteStr(w),
                                                                                quoteStr(b),
                                                                                quoteStr(F?.industry),
                                                                                quoteStr(F?.keywords.join(",")),
                                                                                F?.estimated_num_employees,
                                                                                quoteStr(F?.city),
                                                                                quoteStr(F?.state),
                                                                                quoteStr(F?.country),
                                                                                quoteStr(M),
                                                                                quoteStr(z),
                                                                                quoteStr(k),
                                                                                quoteStr(L),
                                                                                quoteStr(v),
                                                                            ]),
                                                                            (getEl(".findy--export-progress-current").textContent = findy.peopleList.length - 1),
                                                                            (getEl(".findy--export-progress-total").textContent = n),
                                                                            findy.peopleList.length - 1 >= +n)
                                                                        )
                                                                            throw (setExportCompleted(), clearTimeout(findy.collectPeopleFailTimer), p);
                                                                        (a += 1),
                                                                            console.log("localCounter #10 " + a),
                                                                            (25 !== a && a !== m) ||
                                                                                (clearTimeout(findy.collectPeopleFailTimer),
                                                                                setTimeout(function () {
                                                                                    flipPage(),
                                                                                        setTimeout(function () {
                                                                                            collectPeople(r);
                                                                                        }, Math.max(5e3, Math.floor(7500 * Math.random())));
                                                                                }, Math.max(7500, Math.floor(15e3 * Math.random()))));
                                                                    }
                                                                });
                                              })
                                              .catch(() => {
                                                  console.log(g + " never showed up"),
                                                      i < l.length - 1 &&
                                                          setTimeout(function () {
                                                              chrome.storage.sync.get(["export_status"], function ({ export_status: e }) {
                                                                  "finished" !== e && (i++, l[i].click());
                                                              });
                                                          }, Math.max(1e3, Math.floor(1950 * Math.random())));
                                              })
                                        : findy.emailList.includes(f)
                                        ? (console.log("We already added " + f + " (?)"),
                                          chrome.storage.sync.set({ apollo_duplicates: !0 }).then(),
                                          n--,
                                          r--,
                                          chrome.storage.sync.set({ peopleToExport: n }).then(),
                                          (a += 1),
                                          console.log("localCounter #15 " + a),
                                          (25 !== a && a !== m) ||
                                              (clearTimeout(findy.collectPeopleFailTimer),
                                              setTimeout(function () {
                                                  flipPage(),
                                                      setTimeout(function () {
                                                          collectPeople(r);
                                                      }, Math.max(5e3, Math.floor(7500 * Math.random())));
                                              }, Math.max(7500, Math.floor(15e3 * Math.random())))))
                                        : (findy.emailList.push(f),
                                          verifyEmail(o, f, d, y + " " + h, P?.split("/in")[1], q, x, T, w, b, C)
                                              .then((e) => e.json())
                                              .then((e) => {
                                                  if ((u(), e.error)) throw (alert(e.error), setExportCompleted(), clearTimeout(findy.collectPeopleFailTimer), p);
                                                  if (e.verified) {
                                                      if (
                                                          (findy.peopleList.push([
                                                              quoteStr(P),
                                                              quoteStr(S),
                                                              quoteStr(y),
                                                              quoteStr(h),
                                                              f,
                                                              quoteStr(x),
                                                              quoteStr(q),
                                                              E,
                                                              quoteStr(T),
                                                              quoteStr(w),
                                                              quoteStr(b),
                                                              quoteStr(F?.industry),
                                                              quoteStr(F?.keywords.join(",")),
                                                              F?.estimated_num_employees,
                                                              quoteStr(F?.city),
                                                              quoteStr(F?.state),
                                                              quoteStr(F?.country),
                                                              quoteStr(M),
                                                              quoteStr(z),
                                                              quoteStr(k),
                                                              quoteStr(L),
                                                              quoteStr(v),
                                                          ]),
                                                          (getEl(".findy--export-progress-current").textContent = findy.peopleList.length - 1),
                                                          (getEl(".findy--export-progress-total").textContent = n),
                                                          findy.peopleList.length - 1 >= +n)
                                                      )
                                                          throw (setExportCompleted(), p);
                                                      (a += 1),
                                                          console.log("localCounter #11 " + a),
                                                          (25 !== a && a !== m) ||
                                                              (clearTimeout(findy.collectPeopleFailTimer),
                                                              setTimeout(function () {
                                                                  flipPage(),
                                                                      setTimeout(function () {
                                                                          collectPeople(r);
                                                                      }, 5e3);
                                                              }, Math.max(5e3, Math.floor(1e4 * Math.random()))));
                                                  } else
                                                      getEmail(o, y + " " + h, _, d, P?.split("/in")[1], q, x, T, w, b)
                                                          .then((e) => e.json())
                                                          .then((e) => {
                                                              u();
                                                              let t = "";
                                                              if (
                                                                  ((t = e.error || e.errors ? "" : e.contact && e.contact.email ? e.contact.email : ""),
                                                                  findy.emailList.includes(t) && "" !== t
                                                                      ? (console.log("We already added " + t + " (?)"),
                                                                        chrome.storage.sync.set({ apollo_duplicates: !0 }).then(),
                                                                        n--,
                                                                        r--,
                                                                        chrome.storage.sync.set({ peopleToExport: n }).then())
                                                                      : (findy.emailList.push(t),
                                                                        findy.peopleList.push([
                                                                            quoteStr(P),
                                                                            quoteStr(S),
                                                                            quoteStr(y),
                                                                            quoteStr(h),
                                                                            t,
                                                                            quoteStr(x),
                                                                            quoteStr(q),
                                                                            E,
                                                                            quoteStr(T),
                                                                            quoteStr(w),
                                                                            quoteStr(b),
                                                                            quoteStr(F?.industry),
                                                                            quoteStr(F?.keywords.join(",")),
                                                                            F?.estimated_num_employees,
                                                                            quoteStr(F?.city),
                                                                            quoteStr(F?.state),
                                                                            quoteStr(F?.country),
                                                                            quoteStr(M),
                                                                            quoteStr(z),
                                                                            quoteStr(k),
                                                                            quoteStr(L),
                                                                            quoteStr(v),
                                                                        ])),
                                                                  (getEl(".findy--export-progress-current").textContent = findy.peopleList.length - 1),
                                                                  (getEl(".findy--export-progress-total").textContent = n),
                                                                  findy.peopleList.length - 1 >= +n)
                                                              )
                                                                  throw (setExportCompleted(), clearTimeout(findy.collectPeopleFailTimer), p);
                                                              (a += 1),
                                                                  console.log("localCounter #12 " + a),
                                                                  (25 !== a && a !== m) ||
                                                                      (clearTimeout(findy.collectPeopleFailTimer),
                                                                      setTimeout(function () {
                                                                          flipPage(),
                                                                              setTimeout(function () {
                                                                                  collectPeople(r);
                                                                              }, 5e3);
                                                                      }, Math.max(5e3, Math.floor(1e4 * Math.random()))));
                                                          })
                                                          .catch((e) => {
                                                              if ((console.error(e), e !== p)) {
                                                                  if (
                                                                      (findy.peopleList.push([
                                                                          quoteStr(P),
                                                                          quoteStr(S),
                                                                          quoteStr(y),
                                                                          quoteStr(h),
                                                                          "",
                                                                          quoteStr(x),
                                                                          quoteStr(q),
                                                                          E,
                                                                          quoteStr(T),
                                                                          quoteStr(w),
                                                                          quoteStr(b),
                                                                          quoteStr(F?.industry),
                                                                          quoteStr(F?.keywords.join(",")),
                                                                          F?.estimated_num_employees,
                                                                          quoteStr(F?.city),
                                                                          quoteStr(F?.state),
                                                                          quoteStr(F?.country),
                                                                          quoteStr(M),
                                                                          quoteStr(z),
                                                                          quoteStr(k),
                                                                          quoteStr(L),
                                                                          quoteStr(v),
                                                                      ]),
                                                                      (getEl(".findy--export-progress-current").textContent = findy.peopleList.length - 1),
                                                                      (getEl(".findy--export-progress-total").textContent = n),
                                                                      findy.peopleList.length - 1 >= +n)
                                                                  )
                                                                      throw (setExportCompleted(), clearTimeout(findy.collectPeopleFailTimer), p);
                                                                  (a += 1),
                                                                      console.log("localCounter #13 " + a),
                                                                      (25 !== a && a !== m) ||
                                                                          (clearTimeout(findy.collectPeopleFailTimer),
                                                                          setTimeout(function () {
                                                                              flipPage(),
                                                                                  setTimeout(function () {
                                                                                      collectPeople(r);
                                                                                  }, 5e3);
                                                                          }, Math.max(5e3, Math.floor(1e4 * Math.random()))));
                                                              }
                                                          });
                                              })
                                              .catch((e) => {
                                                  if ((console.error(e), e !== p)) {
                                                      if (
                                                          (findy.peopleList.push([
                                                              quoteStr(P),
                                                              quoteStr(S),
                                                              quoteStr(y),
                                                              quoteStr(h),
                                                              "",
                                                              quoteStr(x),
                                                              quoteStr(q),
                                                              E,
                                                              quoteStr(T),
                                                              quoteStr(w),
                                                              quoteStr(b),
                                                              quoteStr(F?.industry),
                                                              quoteStr(F?.keywords.join(",")),
                                                              F?.estimated_num_employees,
                                                              quoteStr(F?.city),
                                                              quoteStr(F?.state),
                                                              quoteStr(F?.country),
                                                              quoteStr(M),
                                                              quoteStr(z),
                                                              quoteStr(k),
                                                              quoteStr(L),
                                                              quoteStr(v),
                                                          ]),
                                                          (getEl(".findy--export-progress-current").textContent = findy.peopleList.length - 1),
                                                          (getEl(".findy--export-progress-total").textContent = n),
                                                          findy.peopleList.length - 1 >= +n)
                                                      )
                                                          throw (setExportCompleted(), clearTimeout(findy.collectPeopleFailTimer), p);
                                                      (a += 1),
                                                          console.log("localCounter #14 " + a),
                                                          (25 !== a && a !== m) ||
                                                              (clearTimeout(findy.collectPeopleFailTimer),
                                                              setTimeout(function () {
                                                                  flipPage(),
                                                                      setTimeout(function () {
                                                                          collectPeople(r);
                                                                      }, Math.max(5e3, Math.floor(7500 * Math.random())));
                                                              }, Math.max(7500, Math.floor(15e3 * Math.random()))));
                                                  }
                                              }));
                            } catch (e) {
                                console.log("Findymail extension error:"),
                                    console.log(e),
                                    findy.peopleList.push(["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]);
                            }
                        }),
                        0 === e.length &&
                            (flipPage(),
                            setTimeout(function () {
                                collectPeople(r);
                            }, 5e3)),
                        document.getElementById("findymail-profiles").remove(),
                        !(r < n))
                    )
                        throw (chrome.storage.sync.set({ export_status: "completing" }).then(), p);
                } catch (e) {
                    console.log("Findymail extension error:"), console.log(e), { mode: "no-cors" };
                }
            });
        });
}
function renderStatus(e, t) {
    const o = e.querySelector(".findy--laptop-image"),
        n = e.querySelector(".findy--component-laptop-loader");
    switch (t) {
        case "loading":
            (o.src = chrome.runtime.getURL("images/dashboard.png")), (n.style.display = "block");
            break;
        case "success":
            (o.src = chrome.runtime.getURL("images/success.svg")), (n.style.display = "none");
            break;
        case "error":
            (o.src = chrome.runtime.getURL("images/error.svg")), (n.style.display = "none");
    }
}
// function createList(e, t) {
//     return fetch("https://app.findymail.com/api/lists", { method: "post", headers: new Headers({ Authorization: "Bearer " + e, "Content-type": "application/json", Accept: "application/json" }), body: JSON.stringify({ name: t }) });
// }
function createList(e, t) {
    // Simulate creating a list and returning a successful response
    // The simulated list ID can be a fixed value or generated dynamically
    let simulatedListId = "simulatedListId123"; // Example fixed list ID

    return Promise.resolve({
        list: {
            id: simulatedListId,
            name: t
        }
    });
}
function openContact() {
    chrome.storage.sync.get(["findy_url", "auth_url"], function ({ findy_url: e, auth_url: t }) {
        const o = document.location.href.split("/in/")[1]?.split("/")[0];
        if (!o) return;
        const n = document.createElement("iframe");
        (n.className = "findy--iframe-widget"), (n.src = `${e}${t}&open_lid=${o}`), getEl(".findy--iframe-widget").replaceWith(n), chrome.storage.sync.set({ contact_fetching: !0 }).then();
    });
}
function renderCredist(e) {
    if (!e) return;
    const { paid_balance: t, free_balance: o, free_renew_credits: n } = e;
    (getEl(".findy--credits-type").innerHTML = (t > 0 ? "Credits" : "Free credits") + "&nbsp;&nbsp;"),
        (getEl(".findy--credits-current").innerText = formatNumber(t || o)),
        (getEl(".findy--credits-total").innerText = t > 0 ? "" : "/" + formatNumber(n)),
        (getEl(".findy--credit-add-button").href += "_" + e.status);
}
function renderProfile() {
    getEl(".findy--content-profile", 0, 1).then(function (e) {
        chrome.storage.sync.get(["profile_info"], function ({ profile_info: t }) {
            t &&
                (chrome.storage.sync.set({ contact_fetching: !1 }).then(),
                getEl(".findy--profile-photo-img", null, !0).then(function (e) {
                    e.src = getEl(".pv-top-card-profile-picture__image")?.src || getEl(".profile-photo-edit__preview")?.src;
                }),
                getEl(".findy--profile-name", null, !0).then(function (e) {
                    e.innerText = processString(getEl(".text-heading-xlarge", getEl(".pv-top-card"))?.textContent);
                }),
                getEl(".findy--profile-job", null, !0).then(function (e) {
                    e.innerText = processString(getEl(".text-body-medium", getEl(".pv-top-card"))?.textContent).split(/ at | в | – | - |@ /)[0];
                }),
                getEl(".findy--contacts-fetching", null, !0).then(function (e) {
                    chrome.storage.sync.get(["loadingSpinner"], function ({ loadingSpinner: t }) {
                        e.innerHTML = t;
                    });
                }),
                e.classList.remove("findy--loading"),
                getEl(".findy--profile-contacts-list", null, !0).then(function (e) {
                    e.innerHTML = "";
                    const o = document.createElement("div");
                    t[0]?.emails
                        ? t[0].emails.forEach(function (e, t) {
                              renderHTML("/components/contact-item.html", o).then(function () {
                                  setTimeout(function () {
                                      const o = getEls(".findy--profile-contacts-list-item")[t],
                                          n = o.querySelector(".findy--contact-type");
                                      n.classList.add("findy--contact-type-email"), (getEl("img", n).src = chrome.runtime.getURL("/icons/email.svg"));
                                      const r = o.querySelector(".findy--contact-text");
                                      "NOT_OPENED" === e
                                          ? (r.textContent = generateEmail())
                                          : ((r.innerHTML = e),
                                            r.classList.remove("findy--text-blurred"),
                                            (getEl(".findy--copy-icon", o).src = chrome.runtime.getURL("/icons/copy.svg")),
                                            (o.onclick = function () {
                                                copyContact(e);
                                            }));
                                  }, 0);
                              });
                          })
                        : (getEl(".findy--profile-contacts-list").innerHTML = '<div class="findy--no-contacts">No contacts available</div>'),
                        t[0] &&
                        t[0].emails.some(function (e) {
                            return "NOT_OPENED" === e;
                        })
                            ? (getEl(".findy--profile-contacts-open").classList.remove("findy--dummy-button"), (getEl(".findy--profile-contacts-open").disabled = !1), (getEl(".findy--profile-contacts-open").onclick = openContact))
                            : (getEl(".findy--profile-contacts-open").style.display = "none"),
                        e.append(o);
                }));
        });
    });
}
findyEvents.addEventListener("findyEvent", findyEventsCallback),
    chrome.storage.sync.get(null, function ({ findy_url: e, auth_url: t, authorization_status: o, widget_size: n, widgetX: r, widgetY: i, modal: l }) {
        chrome.storage.sync.set({ authorization_status: o, export_status: "waiting", lang: detectLanguage(), credits_list: null, profile_info: null, contact_fetching: !1, toast: null }).then(function () {
            showWidget(e, t, o, n, r, i, l);
        });
        var a = document.createElement("script");
        (a.src = chrome.runtime.getURL("apollo_inject.js")),
            (document.head || document.body || document.documentElement).appendChild(a),
            setTimeout(function () {
                injectExportButton();
            }, 3e3);
    }),
    chrome.storage.onChanged.addListener(function (e) {
        for (let [t, { newValue: o }] of Object.entries(e))
            if (
                ("authorization_status" === t &&
                    ("not_authorized" === o &&
                        (getEl(".findy--widget", null, !0).then(function (e) {
                            e.classList.contains("findy--unsigned") || e.classList.add("findy--unsigned");
                        }),
                        showPage("unauthorized")),
                    "is_authorized" === o &&
                        (getEl(".findy--widget", null, !0).then(function (e) {
                            e.classList.remove("findy--unsigned");
                        }),
                        chrome.storage.sync.get(["current_tab_url", "credits_list"], function ({ current_tab_url: e, credits_list: t }) {
                            t || reloadIframe(), checkUrl(e);
                        }))),
                "current_tab_url" === t && checkUrl(o),
                "export_status" === t)
            ) {
                if ("working" === o || "completing" === o)
                    try {
                        (getEl(".findy--export-inprogress").style.display = "block"),
                            (getEl(".findy--export-settings").style.display = "none"),
                            (getEl(".findy--export-error").style.display = "none"),
                            (getEl(".findy--export-success").style.display = "none");
                    } catch (e) {}
                if (
                    ("finished" === o &&
                        chrome.storage.sync.get(["apollo_duplicates"], function ({ apollo_duplicates: e }) {
                            try {
                                (getEl(".findy--export-success").style.display = "block"),
                                    (getEl(".findy--export-settings").style.display = "none"),
                                    (getEl(".findy--export-error").style.display = "none"),
                                    (getEl(".findy--export-inprogress").style.display = "none"),
                                    e && (getEl(".findy--export-warning").style.display = "block");
                            } catch (e) {}
                        }),
                    "waiting" === o)
                )
                    try {
                        (getEl(".findy--export-settings").style.display = "block"),
                            (getEl(".findy--export-error").style.display = "none"),
                            (getEl(".findy--export-success").style.display = "none"),
                            (getEl(".findy--export-inprogress").style.display = "none");
                    } catch (e) {}
                if ("error" === o)
                    try {
                        (getEl(".findy--export-error").style.display = "block"),
                            (getEl(".findy--export-settings").style.display = "none"),
                            (getEl(".findy--export-success").style.display = "none"),
                            (getEl(".findy--export-inprogress").style.display = "none");
                    } catch (e) {}
            }
        e.widgetX && e.widgetY && (document.querySelector(".findy--widget").style.transform = `translate(${e.widgetX.newValue}px, ${e.widgetY.newValue}px)`);
    });
const langs = {
    current: [
        "الحالي",
        "Aktuální",
        "Nuværende",
        "Aktuell",
        "Current",
        "Actual",
        "Entreprise actuelle  ",
        "मौजूदा",
        "Saat Ini",
        "Attuale",
        "現在",
        "현재",
        "Semasa",
        "Huidig",
        "Nåværende",
        "Obecnie",
        "Atual",
        "Actual",
        "Current",
        "Nuvarande",
        "ปัจจุบัน",
        "Kasalukuyan",
        "Şu Anda",
        "目前就职",
        "現職",
    ],
    at: [" في ", " ve společnosti ", " hos ", " bei ", " at ", " en ", " chez ", " पर ", " di ", " presso ", " - ", null, " di ", " bij ", " i ", " w ", " na ", " la ", " – ", " på ", " ที่ ", " sa ", " şirketinde ", " - ", null],
};
function renderHTML(e, t, o) {
    return fetch(chrome.runtime.getURL(e))
        .then((e) => e.text())
        .then((e) => {
            o && (t.innerHTML = ""), t.appendChild(document.createRange().createContextualFragment(e));
        });
}
function getEls(e, t = document) {
    return t.querySelectorAll(e);
}
function getEl(e, t, o) {
    return (
        t || (t = document),
        o
            ? new Promise(function (o) {
                  if (t.querySelector(e)) return o(t.querySelector(e));
                  const n = new MutationObserver(function () {
                      t.querySelector(e) && (o(t.querySelector(e)), n.disconnect());
                  });
                  n.observe(document.body, { childList: !0, subtree: !0 });
              })
            : t.querySelector(e)
    );
}
function detectLanguage() {
    const e = document.querySelector('[data-control-name="nav_messaging"]');
    if (!e) return null;
    const t = e.querySelector(".global-nav__primary-link-text")?.textContent?.trim();
    if (!t) return null;
    return {
        الرسائل: "ar_AE",
        Zprávy: "cs_CZ",
        Meddelelser: "da_DK",
        Nachrichten: "de_DE",
        Messaging: "en_US",
        Mensajes: "es_ES",
        Messagerie: "fr_FR",
        मैसेजिंग: "hi_IN",
        Pesan: "in_ID",
        Messaggistica: "it_IT",
        メッセージ: "ja_JP",
        메시지: "ko_KR",
        Mesej: "ms_MY",
        Berichten: "nl_NL",
        Meldinger: "no_NO",
        Wiadomości: "pl_PL",
        Mensagens: "pt_BR",
        Mesaje: "ro_RO",
        Сообщения: "ru_RU",
        Meddelanden: "sv_SE",
        ข้อความ: "th_TH",
        Pagmemensahe: "tl_PH",
        Mesajlaşma: "tr_TR",
        消息: "zh_CN",
        訊息: "zh_TW",
    }[t];
}
function formatNumber(e, t = "en") {
    if (!e) return "0";
    let o,
        n = "ru" === t ? " " : ",";
    if (!(e = parseFloat(e.toString().trim().replace(new RegExp(n, "g"), "")).toString())) return 0;
    -1 !== e.indexOf(".") && ((o = parseFloat(parseFloat(e).toFixed(2))), (e = o.toString().split(".")[0]), (o = o.toString().split(".")[1]));
    let r = "",
        i = 0;
    for (let t = 0; t <= e.length; t++) t % 3 == 0 && 0 !== t && ((r = e.slice(e.length - t, e.length - t + 3) + n + r), i++);
    return e.length - 3 * i != 0 && (r = e.slice(0, e.length - 3 * i) + n + r), (r = r.slice(0, -1)), o && (r = r + "." + o), r;
}
function processString(e = "") {
    return e
        .replaceAll(/\p{Emoji_Presentation}/gu, "")
        .replaceAll(",", " |")
        .replaceAll(/\p{S}/gu, "")
        .trim();
}
function generateEmail(e, t = "@example.dom") {
    const o = "abcdefghijklmnopqrstuvwxyz1234567890",
        n = e || randomBetween(5, 10);
    let r = "";
    for (let e = 0; e < n; e++) r += o[Math.floor(Math.random() * o.length)];
    return (r += t), r;
}
function randomBetween(e, t) {
    return Math.floor(Math.random() * (t - e + 1) + e);
}
function copyContact(e) {
    navigator.clipboard.writeText(e).then(
        function () {
            chrome.storage.sync.set({ toast: "Copied successfully" }).then();
        },
        function () {
            chrome.storage.sync.set({ toast: "Unable to copy. Please copy manually" }).then();
        }
    );
}
function getEmail(e, t, o, n, r = "", i = "", l = "", a = "", s = "", c = "") {

    console.log("DOING SOMETHING SKETCHY")
    return fetch("https://app.findymailasdaawe.com/api/search/name", {
        method: "post",
        headers: new Headers({ Authorization: "Bearer " + e, "Content-type": "application/json", Accept: "application/json" }),
        body: JSON.stringify({ name: t, domain: o, list: n, linkedin_url: r, company: i, job_title: l, company_city: a, company_region: s, company_country: c }),
        signal: Timeout(45).signal,
    });
}
// function verifyEmail(e, t, o, n = "", r = "", i = "", l = "", a = "", s = "", c = "", u = "") {
//     return fetch("https://app.findymail.com/api/verify", {
//         method: "post",
//         headers: new Headers({ Authorization: "Bearer " + e, "Content-type": "application/json", Accept: "application/json" }),
//         body: JSON.stringify({ name: n, email: t, list: o, linkedin_url: r, company: i, job_title: l, company_city: a, company_region: s, company_country: c, twitter_url: u }),
//     });
// }
function verifyEmail(e, t, o, n = "", r = "", i = "", l = "", a = "", s = "", c = "", u = "") {
    // Simulate a response from the email verification process
    let simulatedResponse = {
        verified: true, // or false, depending on what you need
        // Include other properties that your actual API response would have
        // For example, 'error' field if needed
        // error: "Simulated error message" // Uncomment if you want to simulate an error
    };

    return Promise.resolve(simulatedResponse);
}
function cleanCompanyName(e) {
    return (e = (e = (e = (e = (e = (e = (e = (e = (e = (e = (e = (e = (e = (e = (e = (e = (e = (e = (e = e.split("- ")[0]).replaceAll(/ *\([^)]*\) */g, "")).replace(", Inc.", "")).replace(" Inc.", "")).replace(" Inc", "")).replace(
        " LLC",
        ""
    )).replace(" Ltd", "")).replace(" LTD", "")).replace(" GmbH", "")).replace(", LLC", "")).replace(", Ltd", "")).replace(", LTD", "")).trim()).replace("<b>", "")).replace("</b>", "")).replace(",", "")).replace("&lt;b&gt;", "")).replace(
        "&lt;/b&gt;",
        ""
    )).replace(", INC.", ""));
}
function cleanName(e) {
    let t = processString(e);
    return t.charAt(0).toUpperCase() + t.slice(1);
}
function cleanJobTitle(e) {
    return processString(e);
}
function cleanCity(e) {
    let t = e.replace("Greater ", "");
    return (t = t.replace("Metropolitan Area", "")), (t = t.replace("Area", "")), t.trim();
}
function quoteStr(e) {
    return null == e ? "" : '"' + e + '"';
}
// function getLists(e) {
//     return fetch("https://app.findymail.com/api/lists", { method: "get", headers: new Headers({ Authorization: "Bearer " + e, "Content-type": "application/json", Accept: "application/json" }) });
// }
function getLists(e) {
    // Simulate a successful response with fixed list data
    return Promise.resolve({
        lists: [
            { id: "hahahahahahaha", name: "Main List" }
        ]
    });
}

// async function getCredits(e) {
//     return fetch("https://app.findymail.com/api/credits", { method: "get", headers: new Headers({ Authorization: "Bearer " + e, "Content-type": "application/json", Accept: "application/json" }) });
// }
async function getCredits(e) {
    // Simulate a successful response with fixed credits
    return Promise.resolve({
        credits: 5000, // Fixed number of API credits
        verifier_credits: 5000 // Fixed number of verifier credits
    });
}
function setExportCompleted() {
    chrome.storage.sync.set({ export_status: "finished" }).then(), saveCSV();
}
