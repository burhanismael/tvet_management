odoo.define('tvet_management.student_dashboard_update', function (require) {
'use strict';

var publicWidget = require('web.public.widget');

publicWidget.registry.StudentResulDashboard = publicWidget.Widget.extend({
    selector: '.student_marks_dashboard',
    events: {
        'change .student_marks': '_change_marks',
    },

    _change_marks: function(ev) {
        var self = this;
        var line_id = $(ev.currentTarget).attr('line_id');
        var line_ids = $(ev.currentTarget).attr('line_ids');
        var attr = "span[total_line_ids='" + line_ids + "']";
        var $total_id = $($(ev.currentTarget).parents(".student_tr_m").find(attr))
        $(ev.currentTarget).parents(".student_tr_m").find(attr)
        var marks = $(ev.currentTarget).val();
        return this._rpc({
            route: '/update/student_marks',
            params: {'line_id': line_id, 'value': marks, 'line_ids': line_ids},
        }).then(function(res){
            if(res.total != '0.0'){
                $total_id.text(res.total);
            }
        });
    },
});
});