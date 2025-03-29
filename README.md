## Przygotowanie środowiska

### 1. Instalacja niezbędnych narzędzi

#### OpenTofu (alternatywa dla Terraform)
```bash
# Dla systemów Linux/macOS
brew install opentofu

# Alternatywnie, pobierz z oficjalnej strony:
# https://opentofu.org/docs/intro/install/
```

#### AWS CLI

Zainstaluj AWS CLI, aby móc zarządzać zasobami AWS z poziomu terminala.

https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

#### Git

Upewnij się, że masz zainstalowanego Gita:

```sh
git --version
```

### 2. Klonowanie repozytorium
```sh
git clone https://github.com/deployed/flashcards-workshop-ops.git
```

### 3. Konfiguracja AWS CLI
```sh
aws configure
```
Podaj wymagane informacje:
- AWS Access Key ID: [Twój klucz dostępu]
- AWS Secret Access Key: [Twój sekretny klucz]
- Default region name: eu-west-1
- Default output format: json

### 4. Weryfikacja konfiguracji AWS CLI
```sh
# Sprawdź, czy możesz połączyć się z kontem AWS
aws sts get-caller-identity
```
Powinieneś zobaczyć swoją tożsamość AWS, co potwierdza poprawną konfigurację.

### 5. Inicjalizacja projektu OpenTofu

W katalogu projektu uruchom:
```sh
tofu init
```
Tofu zainstaluje wszystkie wymagane zasoby i przygotuje środowisko do pracy.

### 6. Wykonanie testowego planu
Otwórz plik `required_variables.tf` i uzupełnij wymagane zmienne:

```hcl
# Przykład uzupełnienia zmiennych
variable "group_name" {
  description = "Unikalna nazwa grupy używana jako prefiks zasobów"
  type        = string
  default     = "twoja-nazwa-grupy"
}
```

Zmienne `vpc_id` oraz `vpc_subnet_id` już posiadają wartości default. Nie zmieniaj ich, będą potrzebne do konfiguracji interfejsu sieciowego EC2.

Po uzupełnieniu zmiennych, uruchom:
```bash
tofu plan
```
Jeśli wszystko zostało poprawnie skonfigurowane, plan powinien zostać wygenerowany bez błędów.

### 7. Zalogowanie się do konsoli AWS

Zaloguj się do [konsoli AWS](https://aws.amazon.com/console/).

## Konfiguracja VM - EC2

W tym ćwiczeniu utworzysz maszynę wirtualną EC2 oraz przypiszesz jej interfejs sieciowy i konfigurację firewalla pozwalającą na połączenie z zewnątrz.

### 1. Potrzebne elementy

Zanim stworzysz EC2 potrzebujesz pary kluczy by móc się na nią zalogować. Dodaj klucz publiczny do zmiennej `vm_public_key`.

Tworzenie EC2 jest trochę jak budowa nowego komputera - musisz zebrać elementy które tworzą maszynę wirtualną a potem podać je jako argumenty do zasobu `aws_instance`.

Na potrzeby testowe możesz stworzyć też EC2 bez podawania tych dodatkowych wartości, jednak zostaną wtedy zaaplikowane ustawienia domyślne które nie są szczególnie użyteczne. Aby wyczyścić po testowym deploymencie użyj polecenia `tofu destroy`

Potrzebne będą:
* Definicja pary kluczy SSH (w tofu podajesz tylko klucz publiczny) - instrukcja do wygenerowania kluczy od githuba https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
* Definicja security group wraz z zasadami ingress oraz egress
* Definicja interfejsu sieciowego do którego podłączysz security grupę
* Publiczny adres ip (elastic) skojarzony z maszyną wirtualną

Dodatkowe informacje:
* Skorzystaj z ami: `ami-0fbb72557598f5284`
* Podsieć w której stworzysz maszynę to: `10.42.0.0/24`
* Stwórz instancję typu `t2.micro`

Po stworzeniu vmki
- Spróbuj połączyć się po ssh (default user to admin)
- zainstaluj nginx wykonując polecenia `sudo apt update`, `sudo apt install nginx`
- wykonaj polecenie `sudo systemctl status nginx`
- strona powinna widnieć pod adresem EC2 na porcie 80

Pełną dokumentację providera AWS dla OpenTofu znajdziesz [tutaj](https://search.opentofu.org/provider/opentofu/aws/latest).

## Deployment apki
<!-- TODO: Marcin -->


## AWS Lambda z S3 - Instrukcje krok po kroku

W tym ćwiczeniu utworzysz funkcję Lambda, która czyta z pliku tesktowego przechowywanego w S3 i udostępnia je poprzez HTTP.


### 1. Utworzenie bucketu S3

Zacznij od zdefiniowania bucketu S3, który będzie przechowywał plik tekstowy:

Użyj do tego resource'a [`aws_s3_bucket`](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket).
Jako prefix nazwy bucketu użyj zmiennej `group_name`.

**Jak sprawdzić?** Po wykonaniu `terraform apply` sprawdź, czy bucket został utworzony:
1. Zaloguj się do konsoli AWS
2. Przejdź do usługi S3 (wpisz "S3" w wyszukiwarce)
3. Na liście bucketów znajdź bucket z prefixem odpowiadającym twojej zmiennej `group_name`


### 2. Dodanie pliku do bucketu S3

Załaduj plik tekstowy do bucketu. Plik znajduje się w katalogu `lambda_resources`:

```terraform
resource "aws_s3_object" "random_lines_file" {
  bucket  = [...]
  key     = [...]
  source  = [...]
  etag    = filemd5("${path.module}/lambda_resources/random_lines.txt")
}
```

**Jak sprawdzić?** Po wykonaniu `terraform apply` sprawdź zawartość bucketu:
1. W konsoli AWS przejdź do sekcji S3
2. Kliknij na nazwę utworzonego bucketu
3. Powinieneś zobaczyć plik `random_lines.txt` na liście obiektów

### 3. Utworzenie roli IAM dla funkcji Lambda

Lambda potrzebuje przypisaje roli z odpowiednimi uprawnieniami:

```terraform
resource "aws_iam_role" "lambda_role" {
  name = "${var.group_name}_lambda_s3_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}
```
Ten krok deifiniuje rolę IAM, która pozwala, do której w następnych krokach przypiszemy polityki dostępu do S3. 

**Jak sprawdzić?** Po wykonaniu `terraform apply` sprawdź, czy rola została utworzona:
1. W konsoli AWS przejdź do usługi IAM (wpisz "IAM" w wyszukiwarce)
2. W menu po lewej stronie wybierz "Roles"
3. W polu wyszukiwania wpisz nazwę roli z prefixem `group_name`
4. Rola powinna być widoczna na liście

### 4. Utworzenie polityki dostępu do S3

Teraz musisz utworzyć politykę, która pozwoli funkcji Lambda na odczyt plików z S3:
* Skorzystaj z resource'a [`aws_iam_policy`](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy)
* Potrzebujemy uprawnień `s3:GetObject` oraz `s3:ListBucket`


```terraform
resource "aws_iam_policy" "lambda_s3_policy" {
  name        = "${var.group_name}_lambda_s3_access_policy"
  description = "Allow Lambda to access S3"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = [...]
      Action   = [...]
      Resource = [
        aws_s3_bucket.random_lines_bucket.arn,
        "${aws_s3_bucket.random_lines_bucket.arn}/*"
      ]
    }]
  })
}
```

**Jak sprawdzić?** Po wykonaniu `terraform apply`:
1. W konsoli AWS przejdź do IAM
2. W menu po lewej wybierz "Policies"
3. Wyszukaj politykę z prefixem twojej zmiennej `group_name`
4. Kliknij na nią, aby zobaczyć szczegóły uprawnień

### 5. Podpięcie polityki do roli

Połącz utworzoną rolę z polityką:

```terraform
resource "aws_iam_role_policy_attachment" "lambda_s3" {
  role       = <nazwa_roli>
  policy_arn = <arn_polityki>
}
```

**Jak sprawdzić?** Po wykonaniu `terraform apply`:
1. W konsoli AWS przejdź do IAM
2. Wybierz "Roles" z menu po lewej
3. Znajdź i kliknij na rolę z prefixem `group_name`
4. W zakładce "Permissions" powinna być widoczna dołączona polityka również z prefixem `group_name`

### 6. Przygotowanie paczki z kodem funkcji Lambda

Utwórz archiwum ZIP zawierające kod funkcji Lambda:

* Skorzystaj z resource'a [`archive_file`](https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/archive_file)
* Wykorzystaj plik `random_line_function.py` z katalogu `lambda_resources`
* Wygenerowane archiwum ZIP powinno być zapisane w tym samym katalogu

```terraform
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = [...]
  output_path = [...]
}
```

**Jak sprawdzić?** Po wykonaniu `terraform apply`:
1. Sprawdź lokalnie, czy plik ZIP został utworzony w katalogu `lambda_resources`
2. Możesz otworzyć plik ZIP, aby upewnić się, że zawiera plik `.py`

### 7. Utworzenie funkcji Lambda

Teraz zdefiniuj samą funkcję Lambda:
* Skorzystaj z resource'a [`aws_lambda_function`](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function)
* Użyj roli IAM, którą stworzyłeś wcześniej
* Użyj archiwum ZIP, które stworzyłeś w poprzednim kroku
* Ustaw zmienne środowiskowe `BUCKET_NAME` i `FILE_KEY` na odpowiednie wartości:
  - `BUCKET_NAME` powinien być równy nazwie bucketu S3
  - `FILE_KEY` powinien być równy kluczowi pliku w bucketcie S3

```terraform
resource "aws_lambda_function" "random_line_lambda" {
  function_name    = "${var.group_name}-random-line-function"
  handler          = "random_line_function.lambda_handler"
  role             = <arn_roli>
  runtime          = "python3.10"
  filename         = [...]
  source_code_hash = [...]

  environment {
    variables = {
      BUCKET_NAME = [...]
      FILE_KEY    = [...]
    }
  }
}
```

**Jak sprawdzić?** Po wykonaniu `terraform apply`:
1. W konsoli AWS przejdź do usługi Lambda (wpisz "Lambda" w wyszukiwarce)
2. Na liście funkcji znajdź funkcję z prefixem twojej zmiennej `group_name`
3. Kliknij na funkcję, aby zobaczyć jej szczegóły
4. W zakładce "Configuration" -> "Environment variables" sprawdź, czy zmienne BUCKET_NAME i FILE_KEY zostały poprawnie ustawione

### 8. Konfiguracja URL funkcji Lambda

Aby umożliwić dostęp do funkcji Lambda przez URL:
* Skorzystaj z resource'a [`aws_lambda_function_url`](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function_url)
* Użyj funkcji Lambda, którą stworzyłeś w poprzednim kroku
* Authorization type ustaw na `NONE`, tak aby każdy mógł wywołać funkcję przez URL

```terraform
resource "aws_lambda_function_url" "random_line_lambda_url" {
  function_name      = [...]
  authorization_type = "NONE"
}
```

**Jak sprawdzić?** Po wykonaniu `terraform apply`:
1. W konsoli AWS przejdź do usługi Lambda
2. Kliknij na funkcję z prefixem twojej zmiennej `group_name`
3. W zakładce "Function overview" powinna być widoczna sekcja "Function URL"

### 9. Dodanie uprawnień dla URL funkcji

Lambda wymaga odpowiednich uprawnień, aby można było ją wywoływać przez URL:
* Skorzystaj z resource'a [`aws_lambda_permission`](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_permission)
* Użyj funkcji Lambda, którą stworzyłeś w poprzednim kroku\
* Ustaw `authorization_type` na `NONE`, aby umożliwić publiczny dostęp do funkcji

```terraform
resource "aws_lambda_permission" "function_url" {
  statement_id             = "${var.group_name}_AllowPublicAccess"
  action                   = "lambda:InvokeFunctionUrl"
  function_name            = [...]
  principal                = "*"
  function_url_auth_type   = [...]
}
```

**Jak sprawdzić?** Uprawnienia są niewidoczne bezpośrednio w konsoli, ale można sprawdzić działanie URL:
1. W konsoli AWS przejdź do Lambda
2. Kliknij na funkcję z prefixem twojej zmiennej `group_name`
3. Skopiuj URL funkcji z zakładki "Function URL"
4. Otwórz URL w przeglądarce - jeśli otrzymasz odpowiedź (a nie błąd autoryzacji), oznacza to, że uprawnienia zostały poprawnie skonfigurowane

### 10. Dodanie outputu z adresem URL

Na koniec dodaj output, który wyświetli URL funkcji Lambda po zaaplikowaniu konfiguracji:

```terraform
output "lambda_function_url" {
  value = [...]
}
```

**Jak sprawdzić?** Po wykonaniu `terraform apply`:
1. W terminalu po zakończeniu działania `terraform apply` sprawdź, czy w outputach jest widoczny URL funkcji Lambda
2. Możesz również sprawdzić output za pomocą polecenia `terraform output lambda_function_url`

## Testowanie funkcji Lambda

Po wdrożeniu infrastruktury, możesz przetestować funkcję Lambda:

1. Uruchom `terraform apply` aby wdrożyć infrastrukturę
2. Sprawdź URL funkcji Lambda: `terraform output lambda_function_url`
3. Użyj przeglądarki lub curl do wywołania funkcji:
   ```
   curl $(terraform output -raw lambda_function_url)
   ```
4. Aby uzyskać konkretną linię, dodaj parametr `line_number`:
   ```
   curl "$(terraform output -raw lambda_function_url)?line_number=3"
   ```
