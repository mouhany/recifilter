document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
        tab.setAttribute('aria-selected', 'false');
      });

      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');

      document.querySelectorAll('.content').forEach(content => {
        content.classList.add('d-none');
        content.classList.remove('d-block');
      });

      const contentId = tab.getAttribute('data-content');
      document.getElementById(contentId).classList.remove('d-none');
      document.getElementById(contentId).classList.add('d-block');
    });
  });
});
