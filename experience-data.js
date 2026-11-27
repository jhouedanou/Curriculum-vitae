// Généré par job-bot/outils/maj_experience.py à partir de job-bot/cv.yaml. Ne pas modifier à la main.
// Années d'expérience = mois travaillés (un mois sur deux postes compte une fois), arrondi à l'année inférieure.
window.PERIODES_EXPERIENCE = [{"debut": "2019-06", "fin": null}, {"debut": "2017-06", "fin": "2019-06"}, {"debut": "2017-02", "fin": "2017-06"}, {"debut": "2016-07", "fin": "2017-01"}, {"debut": "2013-08", "fin": "2016-03"}, {"debut": "2013-01", "fin": "2013-06"}, {"debut": "2012-05", "fin": "2012-05"}, {"debut": "2012-05", "fin": "2012-12"}, {"debut": "2009-09", "fin": "2011-04"}];
window.anneesExperience = function (aujourdhui) {
    var d = aujourdhui || new Date(), fin = d.getFullYear() * 12 + d.getMonth(), mois = {};
    var m = function (t) { var p = t.split('-'); return +p[0] * 12 + (+p[1] - 1); };
    window.PERIODES_EXPERIENCE.forEach(function (p) {
        for (var i = m(p.debut); i <= (p.fin ? m(p.fin) : fin); i++) mois[i] = 1;
    });
    return Math.floor(Object.keys(mois).length / 12);
};
window.ANNEES_EXPERIENCE = window.anneesExperience();
