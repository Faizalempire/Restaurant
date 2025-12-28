document.addEventListener('DOMContentLoaded', function() {
  const nameInput = document.getElementById('search-name');
  const typeSelect = document.getElementById('search-type');
  const btn = document.getElementById('search-btn');
  const grid = document.getElementById('restaurants-grid');

  function filter() {
    const q = nameInput.value.trim().toLowerCase();
    const type = typeSelect.value;

    const cards = grid.querySelectorAll('.card');
    cards.forEach(card => {
      const name = card.dataset.name.toLowerCase();
      const cardType = card.dataset.type;
      const matchName = q === '' || name.includes(q);
      const matchType = type === '' || cardType === type;
      card.style.display = (matchName && matchType) ? '' : 'none';
    });
  }

  btn.addEventListener('click', filter);
  nameInput.addEventListener('keyup', function(e) {
    if (e.key === 'Enter') filter();
  });
});
