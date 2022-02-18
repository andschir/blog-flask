$(document).ready(function() {
  if (!!document.getElementById('datetimepicker1')) {
    const picker = new tempusDominus.TempusDominus(document.getElementById('datetimepicker1'), {
      restrictions: {
        minDate: moment().toISOString()
      },
      hooks: {
        inputFormat: (context, date) => {
          return moment(date).format('DD.MM.YYYY, HH:mm')
        }
      },
      display: {
        viewMode: 'clock',
        components: {
          decades: false,
          year: false,
          month: true,
          date: true,
          hours: true,
          minutes: true,
          seconds: false,
          useTwentyfourHour: true,
        }
      },
      stepping: 1,
    });
  }
});
