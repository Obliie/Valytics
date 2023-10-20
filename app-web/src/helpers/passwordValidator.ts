export function passwordValidator(
  password: string,
  state: { value: string; error: string },
  setState: (state: { value: string; error: string }) => void,
  confirmPassword?: string,
) {
  console.log('Password: ' + password);
  console.log('Confirm Password: ' + confirmPassword);

  const trimPassword = password.trim();

  if (!trimPassword) {
    setState({ ...state, error: "Password can't be empty." });
    return false;
  }
  if (trimPassword.length < 8) {
    setState({
      ...state,
      error: 'Password must be at least 8 characters long.',
    });
    return false;
  }

  if (confirmPassword && password !== confirmPassword) {
    setState({ ...state, error: 'Passwords must match.' });
    return false;
  }

  setState({ ...state, error: '' });
  return true;
}
