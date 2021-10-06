const version = "v0.0.8";
const ms_per_day = 1000 * 60 * 60 * 24;

function dateDiffInWeeks(a, b) {
  var utc1 = Date.UTC(a.getFullYear(), a.getMonth(), a.getDate());
  var utc2 = Date.UTC(b.getFullYear(), b.getMonth(), b.getDate());
  var weeks = Math.floor((utc2 - utc1) / ms_per_day) / 7;
  return weeks.toFixed(0);
}

$(document).ready( function () {
    // Github orgainisation table
    $("#org-table").DataTable( {
        ajax: {
            // url: '/github_data_org.json',  // Local testing
            url: 'https://crazy-awesome-crypto-api.infocruncher.com/github_data_org.json',
            dataSrc: 'data'
        },
        initComplete: function(settings, json) {
            var cnt = this.api().data().length.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
            $('#count').text(cnt);
        },
        order: [[ 5, "desc" ]],
        columnDefs: [{ targets:"_all", orderSequence: ["desc", "asc"] }],
        paging: false,
        columns: [
          { title: "Symbol",
            render: function(data, type, row, meta) {
                if (row.ticker == null || row.cmc_name == null) {
                    return ""
                } else {
                    return "<a href='https://coinmarketcap.com/currencies/" + row.cmc_name + "'>" + row.ticker + "</a>";
                }
            }
          },
          { data: "market_cap_usd_mil", title: "Market<br />Cap", className: "text-nowrap", render: $.fn.dataTable.render.number(',', '.', 0, '$', 'M') },
          { title: "Github<br />Organisation",
            render: function(data, type, row, meta) {
                return "<a href='https://github.com/" + row.org + "'>" + row.org + "</a>";
            }
          },
          { data: "repo_count", title: "Project<br />Count" },
          { title: "Top Projects by Stars",
            render: function(data, type, row, meta) {
                var repos = row.repopath_first5.split(",");
                var repos_links = repos.map(repo =>
                    "<a href='https://github.com/" + repo + "' target='_blank'>" +
                    "<img src='img/github.png' class='github-img'></img></a>&nbsp;" +
                    "<a href='https://github.com/" + repo + "'>" + repo.split("/")[1] + "</a>");
                return repos_links.slice(0, 3).join("<br />");
            }
          },
          { data: "stars_max", title: "Max<br />Stars", className: "text-nowrap", render: $.fn.dataTable.render.number(',', '.', 0) },
          { data: "stars_sum", title: "Sum of<br />Stars", className: "text-nowrap", render: $.fn.dataTable.render.number(',', '.', 0) },
          //{ data: "stars_per_week_max", title: "Stars/wk<br />(max)", className: "text-nowrap", render: $.fn.dataTable.render.number(',', '.', 0) },
          { data: "stars_per_week_sum", title: "Sum of<br />Stars/week", className: "text-nowrap", render: $.fn.dataTable.render.number(',', '.', 0) },
          { title: "Project Age<br />Histogram",
            render: function(data, type, row, meta) {
                return row.age_weeks_hist + " weeks";
            }
          },
          //{ data: "stars_hist", title: "Stars<br />Hist", orderable: false },
          { data: "created_at_min", title: "Earliest<br />Created<br />Project",
            className: "text-nowrap",
            render: function(data, type, row, meta) { return new Date(data).toISOString().split('T')[0]; }
          },
          { data: "created_at_max", title: "Latest<br />Created<br />Project",
            className: "text-nowrap",
            render: function(data, type, row, meta) { return new Date(data).toISOString().split('T')[0]; }
          },
          { data: "updated_at_min", title: "Earliest<br />Updated<br />Project",
            className: "text-nowrap",
            render: function(data, type, row, meta) { return new Date(data).toISOString().split('T')[0]; }
          },
          { data: "updated_at_max", title: "Latest<br />Updated<br />Project",
            className: "text-nowrap",
            render: function(data, type, row, meta) { return new Date(data).toISOString().split('T')[0]; }
          },
        ],
    });

    // Github repo table
    $("#repo-table").DataTable( {
        // dom: 'iftrip',  // https://datatables.net/reference/option/dom
        ajax: {
            // url: '/github_data.json',  // Local testing
            url: 'https://crazy-awesome-crypto-api.infocruncher.com/github_data.min.json',
            // url: 'https://crazy-awesome-crypto-api.infocruncher.com/github_data.json',
            dataSrc: 'data'
        },
        initComplete: function(settings, json) {
            var cnt = this.api().data().length.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
            $('#count').text(cnt);
        },
        order: [[ 4, "desc" ]],
        columnDefs: [{ targets:"_all", orderSequence: ["desc", "asc"] }],
        paging: true,
        lengthChange: false,
        lengthMenu: [ 10, 100, 1000, 10000 ],
        pageLength: 100,
        columns: [
          { data: "_readme_localurl", title: "",
            orderable: false,
            render: function(data, type, row, meta) {
                if (data.length > 0) {
                    var url = "/data/" + data + "";
                    return "<img src='img/info2.png' alt='info' class='modal-ajax info-img' href='#' data-localurl='"+url+"' data-ext='.html' data-title='' data-replace-lf='false'></img>";
                } else {
                    return "";
                }
            }
          },
          //{ data: "category", title: "Category" },
//          { data: "_organization", title: "Organisation",
//            render: function(data, type, row, meta) {
//                return "<a href='https://github.com/" + data + "'>" + data.toLowerCase() + "</a>";
//            }
//          },
          { data: "githuburl", title: "Github Project",
            render: function(data, type, row, meta) {
                return "<a href='" + row.githuburl + "'>" + row._repopath.toLowerCase() + "</a>";
            }
          },
          { data: "_description", title: "Description",
            render: function(data, type, row, meta) {
                var desc = row._reponame + ": " + row._description;
                //var desc = "<a href='" + row.githuburl + "'>" + row._reponame + "</a>: "+ row._description;
                return "<div class='text-wrap description-column'>" + desc + "</div>";
            }
          },
          { title: "Links",
            render: function(data, type, row, meta) {
                var repoUrl = "<a href='" + row.githuburl + "' target='_blank'>" + "<img src='img/github.png' class='github-img'></img></a>&nbsp;<a href='" + row.githuburl + "'>" + row._repopath + "</a>";
                var homepageUrl = "";
                try { homepageUrl = "<br /><a href='" + row._homepage + "' target='_blank'><img src='img/web.png' class='web-img'></img></a>&nbsp;<a href='" + row._homepage + "'>" + new URL(row._homepage).hostname + "</a>"; } catch { }
                return repoUrl + homepageUrl;
            }
          },
          { data: "_stars", title: "Stars", className: "text-nowrap", render: $.fn.dataTable.render.number(',', '.', 0) },
          { data: "_stars_per_week", title: "Stars<br />per&nbsp;week",
            render: function(data, type, row, meta) { return data > 10 ? data.toFixed(0) : data.toFixed(1); }
          },
          { data: "_forks", title: "Forks", className: "text-nowrap", render: $.fn.dataTable.render.number(',', '.', 0) },
          { data: "_updated_at", title: "Updated",
            className: "text-nowrap",
            render: function(data, type, row, meta) { return new Date(data).toISOString().split('T')[0]; }
          },
          { data: "_created_at", title: "Created",
            className: "text-nowrap",
            render: function(data, type, row, meta) { return new Date(data).toISOString().split('T')[0]; }
          },
//          { data: "_age_weeks", title: "Age in&nbsp;weeks",
//            render: function(data, type, row, meta) { return data.toFixed(0); }
//          },
          { data: "_updated_at", title: "Weeks<br />since<br />updated",
            className: "text-nowrap",
            render: function(data, type, row, meta) {
                var updated = new Date(data);
                var today = new Date();
                return dateDiffInWeeks(updated, today);
            }
          },
          { data: "_created_at", title: "Weeks<br />since<br />created",
            className: "text-nowrap",
            render: function(data, type, row, meta) {
                var updated = new Date(data);
                var today = new Date();
                return dateDiffInWeeks(updated, today);
            }
          },
          { data: "_language", title: "Primary<br />Language" },
//          { data: "_topics", title: "Tags",
//            render: function(data, type, row, meta) { return data.join(", "); }
//          },
        ],
    });

    $("#repo-table").on('click', '.modal-ajax', function(e) {
        var localurl = $(this).data('localurl') + $(this).data('ext');
        e.preventDefault();

        $.ajax({
           type: "GET",
           url: localurl,
           title: $(this).data('title'),
           replace_lf: $(this).data('replace-lf'),
           success: function(content)
           {
                if (this.replace_lf) {
                    content = content.replace(/\n/g, '<br />');
                }
                var html = "<div class='modal'>";
                if (this.title.length > 0) {
                    html = html + "<b>" + this.title + "</b><br /><br />";
                }
                html = html + content + "</div>";
                $(html).appendTo("#container").modal();
           },
           error: function(html)
           {
                console.log("ERROR getting localurl: " + localurl);
           },
        });

        return false;
    });
});



