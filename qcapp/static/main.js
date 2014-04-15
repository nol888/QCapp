// Great markup here.
var ui = {
    error: function(msg, type) {
        type = type || "Error";
        var d = $('<div class="alert alert-danger alert-dismissable fade in"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button><strong>' + type + ':</strong> </div>');

        d.append(msg);
        d.insertBefore($('#cmdform'));
    },
    log: function(msg) {
        if (console && console.log) {
            console.log(msg);
        }
    },

    inputHistory: [],
    historyPos: -1,
    processInput: function(text) {
        this.historyPos = -1;
        this.inputHistory.unshift(text);

        if ((m = /^(\d{2}:\d{2}) /.exec(text)) != null) {
            time = m[1];
            text = text.substring(time.length + 1);

            api.add(time, text);
        } else if ((m = /^done (\d+)/.exec(text)) != null) {
            api.done(parseInt(m[1]));
        } else if ((m = /^reject (\d+)/.exec(text)) != null) {
            api.reject(parseInt(m[1]));
        } else if ((m = /^reopen (\d+)/.exec(text)) != null) {
            api.reopen(parseInt(m[1]));
        } else {
            this.inputHistory.x.shift();
            this.error(text, "Invalid input");
        }
    },
    inputKeyHandler: function(e) {
        switch (e.keyCode) {
            case 38: // UP
                e.preventDefault();
                if (ui.historyPos < ui.inputHistory.length - 1) {
                    $('#cmdline').val(ui.inputHistory[++ui.historyPos]);
                }
                break;
            case 40: // DOWN
                e.preventDefault();
                if (ui.historyPos > 0) {
                    $('#cmdline').val(ui.inputHistory[--ui.historyPos]);
                }
                else if (ui.historyPos == 0) {
                    ui.historyPos--;
                    $('#cmdline').val('');
                }
                break;
        }
    },

    toggleShow: function() {
        var btn = $('#btn-showall');

        if (btn.hasClass('active')) {
            btn.removeClass('active');
            $('.danger, .item-done').fadeOut();
        } else {
            btn.addClass('active');
            $('.danger, .item-done').fadeIn();
        }
    },

    createRow: function(item) {
        var row = $('<tr></tr>');
        row.append($('<td></td>').text(item.id));
        row.append($('<td></td>').text(item.time));
        row.append($('<td></td>').text(item.text));

        this.updateRow(row, item.status);

        return row;
    },
    appendRow: function(item) {
        $('#maintable > tbody').append(this.createRow(item));
    },
    addRow: function(item) {
        var row = this.createRow(item);
        var rows = $('#maintable > tbody > tr');

        // I hate myself.
        for (i = 0; i < rows.length; i++) {
            if (rows.eq(i).children().eq(1).text() < item.time) {
                continue;
            }

            rows.eq(i).before(row);
            return;
        }

        $('#maintable > tbody').append(row);
    },
    findRow: function(id) {
        return $('#maintable > tbody > tr > td:first-child:contains("' + id + '")').parent();
    },
    updateRow: function(row, status) {
        row.removeClass("info item-done danger");
        switch(status) {
            case 1: // ITEM_NEW
                row.addClass("info");
                break;
            case 2: // ITEM_DONE
                row.addClass("item-done");
                break;
            case 3: // ITEM_REJECTED
                row.addClass("danger");
                break;
        }

        if (status != 1 && !$('#btn-showall').hasClass('active')) {
            row.css('display', 'none');
        }
    },

    refreshTable: function(data) {
        // Manually index each item because I don't know why
        // I made the id implicitly ordered.
        //
        // Probably because I'm a dumbass.
        for (i in data) {
            data[i].id = i;
        }

        // !sux compareTo
        data.sort(function(a, b) {
            if (a.time < b.time) {
                return -1;
            } else if(a.time == b.time) {
                if (a.id < b.id) {
                    return -1;
                } else if (a.id == b.id) {
                    return 0;
                } else {
                    return 1;
                }
            } else {
                return 1;
            }
        });

        $('#maintable > tbody').empty();
        for (i in data) {
            this.appendRow(data[i]);
        }
    }
};

var api = {
    add: function(time, text) {
        ui.log("API call: endpoint=/add, time=" + time + ", text=" + text);

        $.post("/api/add", JSON.stringify({
            'time': time,
            'text': text
        })).fail(function(jqXHR) {
            if (jqXHR.status == 500) {
                e = JSON.parse(jqXHR.responseText);
                ui.error(e.error, "API (/add) call failed");
            } else {
                ui.log("/api/add failed with: " + jqXHR.statusText);
            }
        });
    },

    list: function() {
        ui.log("API call: endpoint=/list");

        $.getJSON("/api/list").done(function(data) {
            ui.refreshTable(data.items);
        }).fail(function(jqXHR) {
            ui.log("/api/list failed with: " + jqXHR.statusText);
        });
    },

    // Yes, I know $.proxy is a thing.
    // However, this object is evaulated before jQuery is available on the DOM,
    // and I don't feel like fixing that.
    done: function(id) { this.__updateStatus("done", id); },
    reject: function(id) { this.__updateStatus("reject", id); },
    reopen: function(id) { this.__updateStatus("reopen", id); },

    __updateStatus: function(verb, id) {
        ui.log("API call: endpoint=/" + verb + ", id=" + id);

        $.post("/api/" + verb + "/" + id).fail(function(jqXHR) {
            if (jqXHR.status == 500) {
                e = JSON.parse(jqXHR.responseText);
                ui.error(e.error, "API (/" + verb + ") call failed");
            } else {
                ui.log("/api/" + verb + " failed with: " + jqXHR.statusText);
            }
        });
    },

    subscribe: function() {
        ui.log("API call: endpoint=/stream");

        this.stream = new EventSource("/api/stream");
        this.stream.addEventListener("add", function(e) {
            ui.addRow(JSON.parse(e.data));
        });
        this.stream.addEventListener("change", function(e) {
            d = JSON.parse(e.data);
            ui.updateRow(ui.findRow(d.id), d.status);
        });
    }
};

$(document).ready(function() {
    // Hook up the command prompt processing.
    $('#cmdform').submit(function(e) {
        e.preventDefault();

        ui.processInput($('#cmdline').val());
        $('#cmdline').val('');
    });

    // Hook up command prompt keypress.
    $('#cmdline').keyup(ui.inputKeyHandler);

    // Hook up the 'show all' button.
    $('#btn-showall').click(function(e) {
        e.preventDefault();
        ui.toggleShow();
    })

    // Make escape clear errors.
    $(document).keyup(function(e) {
        if (e.keyCode == 27) { $('.alert').alert('close'); }
    });

    // Focus command prompt.
    $('#cmdline').focus();

    // Load list of QC items.
    api.list();

    // Subscribe to event stream.
    api.subscribe();
});