odoo.define('tvet_management.portal_my_exam_update', function (require) {
    'use strict';

    var $ = require('jquery');

    $(document).ready(function () {
        if ($('#creditErrorModal').length) {
            $('#creditErrorModal').modal('show');
        }
    });
});
