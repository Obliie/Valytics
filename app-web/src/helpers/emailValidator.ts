export function emailValidator(
  email: string,
  state: { value: string; error: string },
  setState: (state: { value: string; error: string }) => void,
) {
  const trimEmail = email.trim();
  const re = /\S+@\S+\.\S+/;
  if (!trimEmail) {
    setState({ ...state, error: "Email can't be empty." });
    return false;
  }
  if (!re.test(trimEmail)) {
    setState({ ...state, error: 'Ooops! We need a valid email address.' });
    return false;
  }
  setState({ ...state, error: '' });
  return true;
}
