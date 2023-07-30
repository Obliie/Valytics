export function nameValidator(
  name: string,
  state: { value: string; error: string },
  setState: (state: { value: string; error: string }) => void,
) {
  const trimName = name.trim();
  if (!trimName) {
    setState({ ...state, error: "Name can't be empty." });
    return false;
  }
  setState({ ...state, error: '' });
  return true;
}
