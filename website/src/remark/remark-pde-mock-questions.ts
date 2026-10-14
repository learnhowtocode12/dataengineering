type PreprocessorInput = {filePath: string; fileContent: string};

const escapeHtml = (text: string) =>
  text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const formatInline = (text: string) =>
  escapeHtml(text).replace(/`([^`]+)`/g, '<code>$1</code>');

const normalize = (text: string) => text.replace(/\s+/g, ' ').trim();

const renderQuestion = (number: string, block: string) => {
  const answerMatch = block.match(/^\*\*Correct answer:\s*([A-D])\*\*\s*$/m);
  if (!answerMatch || answerMatch.index === undefined) return null;

  const beforeAnswer = block.slice(0, answerMatch.index).replace(/^\*\*Q\d+[a-z]?\.\*\*\s*/, '');
  const optionMatches = [...beforeAnswer.matchAll(/(?:^|\n)[ \t]*([A-D])[).][ \t]*/g)];
  if (optionMatches.length !== 4 || optionMatches.map((match) => match[1]).join('') !== 'ABCD') return null;

  const optionStart = optionMatches[0].index! + optionMatches[0][0].length - optionMatches[0][1].length - 2;
  const prompt = normalize(beforeAnswer.slice(0, optionStart));
  const choices = optionMatches.map((match, index) => ({
    label: match[1],
    text: normalize(beforeAnswer.slice(match.index! + match[0].length, optionMatches[index + 1]?.index ?? beforeAnswer.length)),
  }));
  const correctMatch = block.match(/^\*\*Why ([A-D]) is correct[^*\n]*:\*\*\s*(.*)$/m);
  const wrongReasons = [...block.matchAll(/^[ \t]*-[ \t]*([A-D])[).][ \t]*(.*)$/gm)].map((match) => ({
    label: match[1],
    text: normalize(match[2]),
  }));

  if (
    !prompt ||
    choices.some((choice) => !choice.text) ||
    !correctMatch ||
    correctMatch[1] !== answerMatch[1] ||
    wrongReasons.length !== 3
  ) {
    return null;
  }

  const optionsHtml = choices.map((choice) => {
    const result = choice.label === answerMatch[1] ? 'Correct' : 'Incorrect';
    return `<label class="mock-option mock-option--${result.toLowerCase()}"><input type="radio" name="mock-question-${number}" value="${choice.label}"><strong>${choice.label})</strong> ${formatInline(choice.text)}<span class="mock-option__status">${result}</span></label>`;
  }).join('\n');
  const wrongHtml = wrongReasons.map((reason) =>
    `<li><strong>${reason.label})</strong> ${formatInline(reason.text)}</li>`,
  ).join('\n');

  return [
    `<section class="mock-question" aria-labelledby="mock-question-${number}">`,
    `<p class="mock-question__prompt" id="mock-question-${number}"><strong>Q${number}.</strong> ${formatInline(prompt)}</p>`,
    '<fieldset class="mock-question__options">',
    '<legend>Choose one answer</legend>',
    optionsHtml,
    '</fieldset>',
    `<p class="mock-question__feedback">Correct answer: <strong>${answerMatch[1]}</strong></p>`,
    '<details class="mock-question__explanation">',
    '<summary>Show explanation</summary>',
    `<p><strong>Why ${answerMatch[1]} is correct:</strong> ${formatInline(correctMatch[2])}</p>`,
    '<p><strong>Why the other options are wrong:</strong></p>',
    `<ul>${wrongHtml}</ul>`,
    '</details>',
    '</section>',
  ].join('\n');
};

export default function preprocessPdeMockQuestions({filePath, fileContent}: PreprocessorInput) {
  if (!filePath.includes('pde_certification')) return fileContent;

  const starts = [...fileContent.matchAll(/^\*\*Q(\d+[a-z]?)\.\*\*/gm)];
  if (!starts.length) return fileContent;

  let output = '';
  let cursor = 0;
  starts.forEach((start, index) => {
    const startIndex = start.index!;
    const endIndex = starts[index + 1]?.index ?? fileContent.length;
    output += fileContent.slice(cursor, startIndex);
    output += renderQuestion(start[1], fileContent.slice(startIndex, endIndex)) ?? fileContent.slice(startIndex, endIndex);
    cursor = endIndex;
  });
  return output + fileContent.slice(cursor);
}