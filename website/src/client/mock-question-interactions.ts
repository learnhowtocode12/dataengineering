if (typeof document !== 'undefined') {
  document.addEventListener('click', (event) => {
    const target = event.target;
    if (!(target instanceof Element)) return;

    const submit = target.closest<HTMLButtonElement>('.mock-question__submit');
    const question = submit?.closest<HTMLElement>('.mock-question');
    if (!question?.querySelector('input[type="radio"]:checked')) return;

    question.classList.add('is-submitted');
  });

  document.addEventListener('change', (event) => {
    const target = event.target;
    if (!(target instanceof HTMLInputElement) || target.type !== 'radio') return;

    const question = target.closest<HTMLElement>('.mock-question');
    if (!question) return;

    question.classList.remove('is-submitted');
    question.querySelector('details')?.removeAttribute('open');
  });
}