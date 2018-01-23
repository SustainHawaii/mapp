/**
 * Created by SULEIMAN on 2/10/2015.
 */

$(function () {
    $('input[name="activity"]').change(function () {
        var val = $('input[name="activity"]:checked').val();
        $('.hide-active').hide();
        $('div[id^= "'+val + '-view-"]').show();
    });

    $("#preview-btn").click(function () {
        var grp_name = document.getElementById('group-name').value;
        $('#visual-name').text(grp_name);
        var data_set_name = selected_data_set_name();
        $("#data-set-name").val(data_set_name);
        $("#data-set-id").val(check_selected_data_set());
        $("#data-set-grp").val(grp_name);

        var viz_type = check_viz_type().val();
        if (viz_type === "chart") {
            var chart_type = $('#chart-type').val();
            switch (parseInt(chart_type)) {
                case 0:
                {
                    /* get the current values of selected X-axis and Y-axis*/
                    var bar_x_value = $('[id^="bar-x-"]').val();
                    var bar_y_value = $('[id^="bar-y-"]').val();

                    /* Set the various data required for saving into the database*/
                    $("#data-set-type").val('bar-chart');
                    $("#category").val('charts');
                    $("#selected-fields-x").val(bar_x_value);
                    $("#selected-fields-y").val(bar_y_value);

                    /* Load the bar chart on changing the chart type to bar-chart*/
                    load_bar_chart(bar_x_value, bar_y_value, "#data-preview");
                }
                    break;
                case 1:
                {

                    var new_x = $('[id^="pie-x-"]').val();
                    var new_y = $('[id^="pie-y-"]').val();

                    /* Set the various data required for saving into the database*/
                    $("#category").val('charts');
                    $("#data-set-type").val('pie-chart');
                    $("#selected-fields-x").val(new_x);
                    $("#selected-fields-y").val(new_y);

                    /* Load the pie chart on changing the chart type to pie-chart*/
                    load_pie_chart(new_x, new_y, "#data-preview");
                }
                    break;
                case 2:
                    area_chart();
                    break;
                case 3:
                {
                    line_chart();
                    var line_x = $('[id="line-x"]').val();
                    var line_y = $('[id="line-y"]').val();

                    $("#data-set-type").val('line-chart');
                    $("#selected-fields").val(line_x + ',' + line_y);
                    $('#data-preview').html('').append($('#linechart').html());
                }
                    break;
            }
        } else if (viz_type == 'timeline') {
            var label = $('#timeline-label').val();
            var start = $('#timeline-start').val();
            var end = $('#timeline-end').val();

            $("#data-set-type").val('timeline');
            $("#selected-fields").val(start + ',' + end + ',' + label);
            $('#data-preview').html('').append($('#timeline').html());
        }
        $("#build").removeClass("in active");
        $("#build-click").removeClass("in active");
        $("#preview").addClass("in active");
        $("#preview-click").addClass("in active");
    });

    $("#save-btn").click(function () {
        $.ajax({
            type: "POST",
            url: "/maps-admin/data/addvisualization",
            data: {
                'update': $("#updated").val(),
                'data-set-id': $("#data-set-id").val(),
                'data-set-grp': $("#data-set-grp").val(),
                'data-set-name': $("#data-set-name").val(),
                'data-set-type': $("#data-set-type").val(),
                'category': $("#category").val(),
                'selected-fields-x': $("#selected-fields-x").val(),
                'selected-fields-y': $("#selected-fields-y").val()
            },
            success: function (data) {
                if (data.id) {
                    $("#publish-id").text(data.id);
                    $("#publish-url").val("http://mapp-dev.elasticbeanstalk.com/maps-admin/data/update-visualization/" + data.id);

                    $("#preview").removeClass("in active");
                    $("#preview-click").removeClass("in active");
                    $("#publish").addClass("in active");
                    $("#publish-click").addClass("in active");
                }
            }
        });
    });

    $("#add_viz_btn").click(function () {
        var _var = check_selected_data_set();
        if (_var) {
            var fields = (jQuery.parseJSON(selectedDataSet(_var)))[0];
            var fields_2 = Object.keys((jQuery.parseJSON(selectedDataSet(_var)))[0]);
            var result = {'data': JSON.parse(selectedDataSet(_var)).slice(0, 20)};

            console.log(JSON.stringify(result));

            var keys = [];
            for (var key in fields) {
                if (fields.hasOwnProperty(key)) {
                    keys.push({'data': key});
                }
            }

            var header = '<table id="example" class="display" cellspacing="0" width="100%"><thead><tr>';
            var footer = '<tfoot><tr>';
            for (var h = 0; h < 9; h++) {
                header += '<th>' + fields_2[h] + '</th>';
                footer += '<th>' + fields_2[h] + '</th>';
            }
            var body = '<tbody>';

            header += '</tr></thead>';
            footer += '</tr></tfoot></table>';

            var adata = $('#data-locations-table');
            adata.html(header + footer);

            $("#example").dataTable({
                'data': result,
                'columns': keys
            });
        }
        else {
        }
    });


    $('#chart-type').change(function () {
        var chart_type = $('#chart-type').val();

        switch (parseInt(chart_type)) {
            case 0:
                bar_chart();
                break;
            case 1:
                pie_chart();
                break;
            case 2:
                area_chart();
                break;
            case 3:
                line_chart();
                break;
        }
    });

    function line_chart() {
        $('#sub-main-container').find('[id$="-chart"]').hide();
        $('[id="line-chart"]').show();
    }

    function bar_chart() {
        $('#sub-main-container').find('[id$="-chart"]').hide();
        $('[id="bar-chart"]').show();
    }

    function pie_chart() {
        $('#sub-main-container').find('[id$="-chart"]').hide();
        $('[id="pie-chart"]').show();
    }

    function area_chart() {
        $('#sub-main-container').find('[id$="-chart"]').hide();
        $('[id="area-chart"]').show();
    }

    /* select data series for pie-chart */
    $('[id^="pie-"]').change(function () {
        var obj = $(this).attr('id').split('-').slice(-1)[0];

        var x = $('[id="pie-x-' + obj + '"]').val();
        var y = $('[id="pie-y-' + obj + '"]').val();

        if (x === '' || y === '') {
            d3.select("#piechart svg").remove();
            return false;
        }
        else {
            var new_x = $('[id^="pie-x-"]').val();
            var new_y = $('[id^="pie-y-"]').val();

            load_pie_chart(new_x, new_y, "#piechart");
        }
    });

    /* select data series for area-chart */
    $('[id^="area-"]').change(function () {
        var c_obj = $(this).attr('id').split('-').slice(-1)[0];

        var c_x = $('[id="area-x-' + c_obj + '"]').val();
        var c_y = $('[id="area-y-' + c_obj + '"]').val();

        if (c_x === '' || c_y === '') {
            d3.select("#areachart svg").remove();
            return false;
        }
        else {

            var obj = $(this).attr('id').split('-').slice(-1)[0];

            var new_x = $('[id^="pie-x-"]').val();
            var new_y = $('[id^="pie-y-"]').val();

            var margin = {top: 20, right: 20, bottom: 30, left: 50},
                width = 960 - margin.left - margin.right,
                height = 500 - margin.top - margin.bottom;

            var parseDate = d3.time.format("%d-%b-%y").parse;

            var x = d3.time.scale()
                .range([0, width]);

            var y = d3.scale.linear()
                .range([height, 0]);

            var xAxis = d3.svg.axis()
                .scale(x)
                .orient("bottom");

            var yAxis = d3.svg.axis()
                .scale(y)
                .orient("left");

            var area = d3.svg.area()
                .x(function (d) {
                    return x(d.date);
                })
                .y0(height)
                .y1(function (d) {
                    return y(d.close);
                });

            d3.select("#areachart svg").append("svg");

            var svg = d3.select("#areachart").append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            var id = selectedDataSet(check_selected_data_set());
            var data = JSON.parse(id).slice(0, 15);
            data.forEach(function (d) {
                d.date = parseDate(d.date);
                d.close = +d.close;
            });

            x.domain(d3.extent(data, function (d) {
                return d.date;
            }));
            y.domain([0, d3.max(data, function (d) {
                return d.close;
            })]);

            svg.append("path")
                .datum(data)
                .attr("class", "area")
                .attr("d", area);

            svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + height + ")")
                .call(xAxis);

            svg.append("g")
                .attr("class", "y axis")
                .call(yAxis)
                .append("text")
                .attr("transform", "rotate(-90)")
                .attr("y", 6)
                .attr("dy", ".71em")
                .style("text-anchor", "end")
                .text("Price ($)");


        }
    });

    $('[id^="bar-"]').change(function () {
        var c_obj = $(this).attr('id').split('-').slice(-1)[0];

        var x = $('[id="bar-x-' + c_obj + '"]').val();
        var y = $('[id="bar-y-' + c_obj + '"]').val();

        if (x === '' || y === null) {
            d3.select("#barchart svg").remove();
            return false;
        }
        else {
            var new_x = $('[id^="bar-x-"]').val();
            var new_y = $('[id^="bar-y-"]').val();
            load_bar_chart(new_x, new_y, "#barchart");
        }
    });

    // changing data series for LINE
    $('[id^="line-"]').change(function () {
        var x = $('[id="line-x"]').val();
        var y = $('[id="line-y"]').val();

        if (!(x == '' || y == '')) {
            load_line_chart(x, y, '#linechart');
        }
    });
    function load_line_chart(x, y, div) {
        var id = selectedDataSet(check_selected_data_set());
        var data = JSON.parse(id).slice(0, 15);
        var lineData = [];
        var y_ticks = 10;

        for (d in data) {
            lineData.push({'x': data[d][x], 'y': data[d][y]});
        }
        lineData.sort(function (a, b) {
            return a.x - b.x;
        });
        var margin = {top: 50, right: 20, bottom: 30, left: 50},
            width = 500 - margin.left - margin.right,
            height = 300 - margin.top - margin.bottom;

        var scale_x = d3.scale.linear()
            .range([0, width]);

        var scale_y = d3.scale.linear()
            .range([height, 0]);

        scale_x.domain(d3.extent(lineData, function (d) {
            return d.x;
        }));
        scale_y.domain(d3.extent(lineData, function (d) {
            return d.y;
        }));

        var xAxis = d3.svg.axis()
            .scale(scale_x)
            .orient("bottom");

        var yAxis = d3.svg.axis()
            .scale(scale_y)
            .ticks(y_ticks)
            .orient("left");

        var line = d3.svg.line()
            .x(function (d) {
                return scale_x(d.x);
            })
            .y(function (d) {
                return scale_y(d.y);
            });

        d3.select(div + " svg").remove();
        var svg = d3.select(div)
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        svg.append("path")
            .attr("class", "axis")
            .attr("fill", "none")
            .attr("stroke", "#000")
            .attr("d", line(lineData));

        svg.selectAll("dot")
            .data(lineData)
            .enter().append("circle")
            .attr("r", 3.5)
            .attr("cx", function(d) { return scale_x(d.x); })
            .attr("cy", function(d) { return scale_y(d.y); });

        svg.append("g")
            .attr("class", "line-axis")
            .attr("transform", "translate(0," + height + ")")
            .attr("fill", "#fff")
            .call(xAxis);

        svg.append("text")
            .attr("class", "x label")
            .attr("text-anchor", "middle")
            .attr("x", width / 2)
            .attr("y", height + margin.bottom)
            .attr("fill", "#fff")
            .text(x);

        svg.append("g")
            .attr("class", "y line-axis")
            .attr("fill", "#fff")
            .call(yAxis);

        svg.append("text")
            .attr("class", "y label")
            .attr("text-anchor", "middle")
            .attr("x", -0.75 * margin.left)
            .attr("y", height / 2)
            .attr("fill", "#fff")
            .text(y);
        for (var j=0; j <= height; j=j+height/(y_ticks -2)) {
            svg.append("svg:line")
                .attr("x1", 0)
                .attr("y1", j)
                .attr("x2", width)
                .attr("y2", j)
                .style("stroke", "#fff")
                .style("stroke-width", 1);
        };

    }

    // changing data series for TIMELINE
    $('[id^="timeline-"]').change(function () {

        var label = $('#timeline-label').val();
        var start = $('#timeline-start').val();
        var end = $('#timeline-end').val();

        if (start == '' || end == '') {
        } else {
            // plot timeline
            load_timeline(start, end, label, "#timeline");
        }
    });
    function load_timeline(start, end, label, div) {
        var id = selectedDataSet(check_selected_data_set());
        var data = JSON.parse(id).slice(0, 15);

        var timeline_data = [{'times': []}];
        for (d in data) {
            timeline_data[0].times.push({
                'starting_time': Date.parse(data[d][start]),
                'ending_time': Date.parse(data[d][end]),
                'label': data[d][label]
            });
        }
        var width = 500;
        var chart = d3.timeline();
        d3.select(div + " svg").remove();
        var svg = d3.select(div).append("svg")
            .attr("width", width)
            .datum(timeline_data)
            .call(chart);
    }
});


function check_selected_data_set() {
    var data_build_source = document.getElementById('data-selected-source');
    if (data_build_source.options[0].selected) {
        return data_build_source.options[0].id;
    }
}

function selected_data_set_name() {
    var data_build_source = document.getElementById('data-selected-source');
    if (data_build_source.options[0].selected) {
        return data_build_source.options[0].text;
    }
}

function check_viz_type() {
    var check = $('input[name="activity"]:checked');
    if (check) {
        return check;
    }
}

function selectedDataSet(elem) {
    return $.ajax({
        url: '/api/v1/dataimport/get-data/' + elem,
        type: 'get',
        global: false,
        async: false,
        success: function (data) {
            return data.results;
        }
    }).responseText;
}

function load_pie_chart(new_x, new_y, div) {
    var width = 860, height = 500, radius = Math.min(width, height) / 2;

    var color = d3.scale.ordinal().range(["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"]);

    var arc = d3.svg.arc().outerRadius(radius - 10).innerRadius(0);

    var pie = d3.layout.pie().sort(null).value(function (d) {
        return d[new_y];
    });

    d3.select(div + " svg").remove();

    var svg = d3.select(div).append("svg")
        .attr("width", width).attr("height", height).append("g")
        .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

    var id = selectedDataSet(check_selected_data_set());
    var data = JSON.parse(id).slice(0, 15);

    data.forEach(function (d) {
        d[new_y] = +d[new_y];
    });

    var g = svg.selectAll(".arc").data(pie(data)).enter().append("g").attr("class", "arc");

    g.append("path").attr("d", arc).style("fill", function (d) {
        return color(d.data[new_x]);
    });

    g.append("text").attr("transform", function (d) {
        return "translate(" + arc.centroid(d) + ")";
    }).attr("dy", ".35em").style("text-anchor", "middle").text(function (d) {
        return d.data[new_x];
    });
}

function load_bar_chart(new_x, new_y, div) {
    var margin = {
            top: 20, right: 20, bottom: 30, left: 40
        },
        width = 1260 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

    var x = d3.scale.ordinal().rangeRoundBands([0, width], .1);
    var y = d3.scale.linear().rangeRound([height, 0]);

    var color = d3.scale.ordinal().range(["#6b486b", "#a05d56", "#d0743c", "#ff8c00", "lightpink", "darkgray", "lightblue"]);

    var xAxis = d3.svg.axis().scale(x).orient("bottom");
    var yAxis = d3.svg.axis().scale(y).orient("left").tickFormat(d3.format(".2s"));

    d3.select(div + " svg").remove();

    var svg = d3.select(div).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var id = selectedDataSet(check_selected_data_set());
    var data = JSON.parse(id).slice(0, 15);

    color.domain(d3.keys(data[0]).filter(function (key) {
        for (var res = 0; res < new_y.length; res++) {
            if (key == new_y[res]) {
                return true;
            }
        }
    }));

    data.forEach(function (d) {
        delete d['import_id'];
        delete d['id'];

        var y0 = 0;
        d.ages = color.domain().map(function (name) {
            return {name: name, y0: y0, y1: y0 += +d[name]};
        });
        d.total = d.ages[d.ages.length - 1].y1;
    });

    data.sort(function (a, b) {
        return b.total - a.total;
    });

    x.domain(
        data.map(function (d) {
            return d[new_x];
        })
    );
    y.domain(
        [0, d3.max(data, function (d) {
            return d.total;
        })]
    );

    svg.append("g").attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")").call(xAxis);

    svg.append("g").attr("class", "y axis")
        .call(yAxis).append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6).attr("dy", ".71em")
        .style("text-anchor", "end").text(x);

    var state = svg.selectAll(".state").data(data).enter().append("g")
        .attr("class", "g").attr("transform", function (d) {
            return "translate(" + x(d[new_x]) + ",0)";
        });

    state.selectAll("rect")
        .data(function (d) {
            return d.ages;
        })
        .enter()
        .append("rect")
        .attr("width", x.rangeBand())
        .attr("y", function (d) {
            return y(d.y1);
        })
        .attr("height", function (d) {
            return y(d.y0) - y(d.y1);
        })
        .style("fill", function (d) {
            return color(d.name);
        });

    var legend = svg.selectAll(".legend").data(color.domain().slice().reverse())
        .enter().append("g").attr("class", "legend")
        .attr("transform", function (d, i) {
            return "translate(0," + i * 20 + ")";
        });

    legend.append("rect").attr("x", width - 18)
        .attr("width", 18).attr("height", 18).style("fill", color);

    legend.append("text").attr("x", width - 24)
        .attr("y", 9).attr("dy", ".35em")
        .style("text-anchor", "end")
        .text(function (d) {
            return d;
        });
}

function load_table_chart() {

}

function load_area_chart() {

}

